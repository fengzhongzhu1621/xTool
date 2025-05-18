from django.utils.translation import gettext_lazy as _lazy

MYSQL_COMMON_SQL_STATEMENTS = [
    {
        "name": _lazy("查询链接信息"),
        "sql": "select * from information_schema.processlist limit 1;",
    },
    {
        "name": _lazy("查看主从信息"),
        "sql": "show slave status;",
    },
    {
        "name": _lazy("当前连接线程"),
        "sql": "show processlist;",
    },
    {
        "name": _lazy("查询版本"),
        "sql": "show variables like 'version';",
    },
    {
        "name": _lazy("查询字符集"),
        "sql": "show variables like 'character_set%';",
    },
    {
        "name": _lazy("查询最大连接数"),
        "sql": "show variables like 'max_connections';",
    },
    {
        "name": _lazy("查询binlog是否打开"),
        "sql": "show variables like 'log_bin';",
    },
    {
        "name": _lazy("查询binlog格式"),
        "sql": "show variables like 'binlog_format';",
    },
    {
        "name": _lazy("慢查询阈值"),
        "sql": "show variables like 'long_query_time';",
    },
    {
        "name": _lazy("库查询"),
        "sql": "show databases;",
    },
    {
        "name": _lazy("innodb缓冲池大小"),
        "sql": "show variables like 'innodb_buffer_pool_size';",
    },
    {
        "name": _lazy("innodb数据文件位置"),
        "sql": "show variables like 'innodb_data_file_path';",
    },
    {
        "name": _lazy("库查询"),
        "sql": "show databases;",
    },
    {
        "name": _lazy("已存在账户查询"),
        "sql": "select concat(User,'@',Host) from mysql.user limit 1000;",
    },
    {
        "name": _lazy("校验结果查询"),
        "sql": (
            "select count(*) from infodba_schema.checksum where this_crc<>master_crc or this_cnt<>master_cnt limit 1;"
        ),
    },
    {
        "name": _lazy("查询唯一索引"),
        "sql": (
            "select distinct table_schema, table_name, index_name, "
            "group_concat(distinct column_name order by seq_in_index) as column_list "
            "from information_schema.statistics  where {table_sts} and {db_sts} and non_unique = 0 "
            "group by table_name, index_name;"
        ),
    },
    {
        "name": _lazy("查询所有表的所有字段类型"),
        "sql": (
            "select table_schema, table_name, column_name, column_type "
            "from information_schema.columns where {table_sts} and {db_sts};"
        ),
    },
    {
        "name": _lazy("根据库名查询表名"),
        "sql": (
            "select table_schema as table_schema, table_name as table_name "
            "from information_schema.tables where {db_sts};"
        ),
    },
]


SQLSERVER__COMMON_SQL_STATEMENTS = [
    {
        "name": _lazy("查询链接信息"),
        "sql": "select loginame,count(1) as cnt from master.sys.sysprocesses "
        "where loginame not in('sa','monitor','dbm_admin') and loginame not like 'mssql%'  "
        "and loginame not like '%\\%'  group by loginame;",
    },
    {
        "name": _lazy("查看主从同步-镜像架构"),
        "sql": "select d.database_id,d.name,create_date,collation_name,state_desc,is_read_only,recovery_model_desc,"
        "m.mirroring_state_desc,mirroring_role_desc,mirroring_safety_level_desc,mirroring_partner_name,"
        "c.cntr_value as log_send_queue_kb from master.sys.databases d "
        "left join master.sys.database_mirroring m on m.database_id=d.database_id "
        "left join master.sys.dm_os_performance_counters c on d.name=c.instance_name and "
        "object_name LIKE '%Database Mirroring%'  AND c.counter_name='Log Send Queue KB' "
        "and c.instance_name not in('_Total') where m.database_id>4 and d.name not in('Monitor');",
    },
    {
        "name": _lazy("查看主从同步-Alwayson架构"),
        "sql": "select d.database_id,d.name,create_date,collation_name,state_desc,is_read_only,recovery_model_desc,"
        "m.replica_id,r.replica_server_name,r.join_state_desc,s.role_desc,s.connected_state_desc,"
        "s.synchronization_health_desc,m.synchronization_state_desc,m.synchronization_health_desc,"
        "m.secondary_lag_seconds as log_send_queue_kb from master.sys.databases d "
        "left join master.sys.dm_hadr_database_replica_states m on m.database_id=d.database_id "
        "left join master.sys.dm_hadr_availability_replica_states s on m.replica_id=s.replica_id "
        "left join master.sys.dm_hadr_availability_replica_cluster_states r on m.replica_id=r.replica_id "
        "where m.database_id>4 and d.name not in('Monitor') order by database_id,role_desc;",
    },
]
