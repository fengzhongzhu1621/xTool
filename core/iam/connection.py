from typing import List

from django.db import connections
from prettytable import PrettyTable

from xTool.db.torndb import TorndbConnection


def get_pymysql_connection(db_name):
    """根据DB名称获取连接对象 ."""
    connection = connections[db_name]
    pymysql_conn = connection.connection
    return pymysql_conn


def ping(reconnect=True):
    """DB重连 ."""
    for db_name in connections.databases.keys():
        conn = get_pymysql_connection(db_name)
        if not conn:
            continue
        conn.ping(reconnect=reconnect)


def execute_query_sql(db_name: str, sql: str, *args, **kwargs) -> List:
    settings_dict = connections[db_name].settings_dict
    conn = TorndbConnection(
        settings_dict["HOST"],
        int(settings_dict["PORT"]),
        settings_dict["NAME"],
        settings_dict["USER"],
        settings_dict["PASSWORD"],
    )
    result = conn.query(sql, *args, **kwargs)

    return result


def print_sql_execute_result(db_name: str, sql: str, *args, **kwargs) -> None:
    result = execute_query_sql(db_name, sql, *args, **kwargs)
    if not result:
        return []
    titles = list(result[0].keys())
    table = PrettyTable(titles)
    for row in result:
        table.add_row(list(row.values()))
    # 左对齐
    table.align = 'l'

    print(table)
