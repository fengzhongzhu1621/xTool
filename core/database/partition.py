import calendar
from datetime import timedelta

from django.db import connection
from django.db.utils import OperationalError
from django.utils import timezone

from apps.logger import logger

__all__ = ["create_month_partitions", "delete_month_partitions"]


def create_month_partitions(table_name: str, num: int = 12) -> None:
    """添加新分区 ."""
    sql_list = []
    cursor = connection.cursor()
    current_month = timezone.now()
    for _ in range(0, num):
        next_month = current_month + timedelta(days=calendar.monthrange(current_month.year, current_month.month)[1])
        sql = "ALTER TABLE {} ADD PARTITION (PARTITION p{} VALUES LESS THAN (TO_DAYS('{}')) ENGINE = InnoDB)"
        sql = sql.format(
            table_name, "{}".format(current_month.strftime("%Y%m")), "{}-01".format(next_month.strftime("%Y-%m"))
        )
        sql_list.append(sql)

        current_month = next_month

    for sql in sql_list:
        try:
            logger.info(sql)
            cursor.execute(sql)
        except OperationalError as exc_info:
            if (
                "Duplicate partition name" in str(exc_info)
                or "Partition management on a not partitioned table is not possible" in str(exc_info)
                or "VALUES LESS THAN value must be strictly increasing for each partition" in str(exc_info)
            ):
                continue
            raise


def delete_month_partitions(table_name: str, days: int) -> None:
    """删除过期的分区."""
    cursor = connection.cursor()
    now = timezone.now()
    delete_month = now - timedelta(days=days)
    sql = "ALTER TABLE {} DROP PARTITION p{}".format(table_name, delete_month.strftime("%Y%m"))
    logger.info(sql)
    try:
        cursor.execute(sql)
    except OperationalError as exc_info:
        if "Error in list of partitions to DROP" in str(
            exc_info
        ) or "Partition management on a not partitioned table is not possible" in str(exc_info):
            pass
        else:
            raise
