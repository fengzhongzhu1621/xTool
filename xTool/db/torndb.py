#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""A lightweight wrapper around MySQLdb.

Originally part of the Tornado framework.  The tornado.database module
is slated for removal in Tornado 3.0, and it is now available separately
as torndb.
"""

import logging
import sys
import time

import pymysql as MySQLdb

PY3 = sys.version_info[0] == 3


version = "2.0"  # pylint: disable=invalid-name


class TorndbConnection:
    """A lightweight wrapper around MySQLdb DB-API connections.

    The main value we provide is wrapping rows in a dict/object so that
    columns can be accessed by name. Typical usage::

        db = torndb.Connection("localhost", "mydatabase")
        for article in db.query("SELECT * FROM articles"):
            print article.title

    Cursors are hidden by the implementation, but other than that, the methods
    are very similar to the DB-API.

    We explicitly set the timezone to UTC and assume the character encoding to
    UTF-8 (can be changed) on all connections to avoid time zone and encoding errors.

    The sql_mode parameter is set by default to "traditional", which "gives an error instead of a warning"
    (http://dev.mysql.com/doc/refman/5.0/en/server-sql-mode.html). However, it can be set to
    any other mode including blank (None) thereby explicitly clearing the SQL mode.

    Arguments read_timeout and write_timeout can be passed using kwargs, if
    MySQLdb version >= 1.2.5 and MySQL version > 5.1.12.
    """

    DRIVER_MAP = {'mysql': 'MySQLdb', 'mssql': 'pymssql', 'oracle': 'cx_Oracle', 'postgresql': 'psycopg2'}

    def __init__(
        self,
        host,
        port,
        database,
        user=None,
        password=None,
        max_idle_time=7 * 3600,
        connect_timeout=0,
        time_zone="+0:00",
        charset="utf8",
        sql_mode="TRADITIONAL",
        autocommit=True,
        **kwargs,
    ):
        self.driver = kwargs.get("driver")
        if self.driver:
            kwargs.pop('driver')
        if not self.driver:
            self.driver = "mysql"
        if self.driver == "mysql":
            self._schema = MySQLdb
        else:
            if self.driver == 'postgres':
                self.driver = 'postgresql'
            self._schema = __import__(self.DRIVER_MAP.get(self.driver))

        self.host = host
        self.port = port
        self.database = database
        self.max_idle_time = float(max_idle_time)
        self.charset = charset
        self.time_zone = time_zone
        self.supports_autocommit = autocommit

        if PY3 and not connect_timeout:
            connect_timeout = 5

        if self.driver == "mysql":
            args = dict(
                use_unicode=True,
                charset=charset,
                port=port,
                db=database,
                init_command=('SET time_zone = "%s"' % time_zone),
                connect_timeout=connect_timeout,
                sql_mode=sql_mode,
                **kwargs,
            )
            if password is not None:
                args["passwd"] = password
        elif self.driver == 'postgresql':
            args = {}
            if password is not None:
                args["password"] = password
            args['dbname'] = database

        if user is not None:
            args["user"] = user

        # We accept a path to a MySQL socket file or a host(:port) string
        if "/" in host:
            args["unix_socket"] = host
        else:
            args["host"] = host
            self.socket = None

        self._db = None
        self._db_args = args
        self._last_use_time = time.time()
        try:
            self.reconnect()
        except Exception:  # pylint: disable=broad-except
            logging.exception("Cannot connect to db on %s", self.host)

    def __del__(self):
        self.close()

    def close(self):
        """Closes this database connection."""
        if getattr(self, "_db", None) is not None:
            self._db.close()
            self._db = None

    def reconnect(self):
        """Closes the existing database connection and re-opens it."""
        self.close()
        print(f"connect {self._db_args}")
        self._db = self._schema.connect(**self._db_args)
        self.autocommit(self.supports_autocommit)
        if self.driver == 'postgresql':
            self.set_charset(self.charset)
            self.set_time_zone(self.time_zone)

    def iter(self, query, *parameters, **kwparameters):
        """Returns an iterator for the given query and parameters."""
        self._ensure_connected()
        cursor = MySQLdb.cursors.SSCursor(self._db)
        try:
            self._execute(cursor, query, parameters, kwparameters)
            column_names = [d[0] for d in cursor.description]
            for row in cursor:
                yield Row(zip(column_names, row))
        finally:
            cursor.close()

    def query(self, query, *parameters, **kwparameters):
        """Returns a row list for the given query and parameters."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters, kwparameters)
            column_names = [d[0] for d in cursor.description]
            return [Row(zip(column_names, row)) for row in cursor]
        finally:
            cursor.close()

    def get(self, query, *parameters, **kwparameters):
        """Returns the (singular) row returned by the given query.

        If the query has no results, returns None.  If it has
        more than one result, raises an exception.
        """
        rows = self.query(query, *parameters, **kwparameters)
        if not rows:
            return None
        elif len(rows) > 1:
            raise Exception("Multiple rows returned for Database.get() query")
        else:
            return rows[0]

    # rowcount is a more reasonable default return value than lastrowid,
    # but for historical compatibility execute() must return lastrowid.
    def execute(self, query, *parameters, **kwparameters):
        """Executes the given query, returning the lastrowid from the query."""
        return self.execute_lastrowid(query, *parameters, **kwparameters)

    def execute_lastrowid(self, query, *parameters, **kwparameters):
        """Executes the given query, returning the lastrowid from the query."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters, kwparameters)
            return cursor.lastrowid
        finally:
            cursor.close()

    def execute_rowcount(self, query, *parameters, **kwparameters):
        """Executes the given query, returning the rowcount from the query."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters, kwparameters)
            return cursor.rowcount
        finally:
            cursor.close()

    def executemany(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the lastrowid from the query.
        """
        return self.executemany_lastrowid(query, parameters)

    def executemany_lastrowid(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the lastrowid from the query.
        """
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.lastrowid
        finally:
            cursor.close()

    def executemany_rowcount(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the rowcount from the query.
        """
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.rowcount
        finally:
            cursor.close()

    update = delete = execute_rowcount
    updatemany = executemany_rowcount

    insert = execute_lastrowid
    insertmany = executemany_lastrowid

    def _ensure_connected(self):
        # Mysql by default closes client connections that are idle for
        # 8 hours, but the client library does not report this fact until
        # you try to perform a query and it fails.  Protect against this
        # case by preemptively closing and reopening the connection
        # if it has been idle for too long (7 hours by default).
        if self._db is None or (time.time() - self._last_use_time > self.max_idle_time):
            self.reconnect()
        self._last_use_time = time.time()

    def _cursor(self):
        self._ensure_connected()
        return self._db.cursor()

    def _execute(self, cursor, query, parameters, kwparameters):
        try:
            return cursor.execute(query, kwparameters or parameters)
        except MySQLdb.OperationalError as e:
            logging.error("Error connecting to MySQL on %s", self.host)
            logging.exception(e)
            self.close()
            raise

    def autocommit(self, flag=True):
        if self.driver == 'mysql':
            self._db.autocommit(flag)
        elif self.driver == 'postgresql':
            self._db.autocommit = self.supports_autocommit

    set_autocommit = autocommit

    def commit(self):
        self._db.commit()

    def rollback(self):
        self._db.rollback()

    def set_charset(self, charset):
        if self.driver == 'postgresql':
            self._db.set_client_encoding(charset)

    def set_time_zone(self, time_zone):
        self.update("set time zone '%s'" % time_zone)


class Row(dict):
    """A dict that allows for object-like property access syntax."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
