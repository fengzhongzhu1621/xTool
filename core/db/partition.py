import calendar
from datetime import timedelta
from typing import List

from django.db import connection
from django.db.utils import OperationalError
from django.utils import timezone

from apps.logger import logger


def create_partitions(table_name: str, dray_run=False) -> List:
    """以月为单位创建分区创建分区 ."""
    sql_list = []
    now = timezone.now()
    current_month = now
    for _ in range(0, 12):
        # 计算下个月
        next_month = current_month + timedelta(days=calendar.monthrange(current_month.year, current_month.month)[1])
        sql = (
            "ALTER TABLE %s ADD PARTITION (PARTITION {} VALUES LESS THAN (TO_DAYS('{}')) ENGINE = InnoDB)"
        ) % table_name
        # 生成分区名
        partition_name = "p{}".format(current_month.strftime("%Y%m"))
        sql = sql.format(partition_name, "{}-01".format(next_month.strftime("%Y-%m")))
        sql_list.append(sql)

        current_month = next_month

    if dray_run:
        return sql_list

    cursor = connection.cursor()
    for sql in sql_list:
        try:
            logger.info(sql)
            cursor.execute(sql)
        except OperationalError as exc_info:
            if "Duplicate partition name" in str(exc_info):
                continue
            raise

    return sql_list


def delete_partitions(table_name: str, rolling_days: int = 90, dray_run=False) -> str:
    """删除历史分区."""

    now = timezone.now()
    delete_month = now - timedelta(days=rolling_days)
    partition_name = "p{}".format(delete_month.strftime("%Y%m"))
    sql = "ALTER TABLE {} DROP PARTITION {}".format(table_name, partition_name)
    logger.info(sql)

    if dray_run:
        return sql

    cursor = connection.cursor()
    try:
        cursor.execute(sql)
    except OperationalError as exc_info:
        if "Error in list of partitions to DROP" in str(exc_info):
            pass
        else:
            raise

    return sql
