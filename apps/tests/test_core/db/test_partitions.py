from core.db import create_partitions, delete_partitions


def test_create_partitions():
    actual = create_partitions("table_name", dray_run=True)
    expect = [
        "ALTER TABLE table_name ADD PARTITION (PARTITION p202405 VALUES LESS THAN "
        "(TO_DAYS('2024-06-01')) ENGINE = InnoDB)",
        "ALTER TABLE table_name ADD PARTITION (PARTITION p202406 VALUES LESS THAN "
        "(TO_DAYS('2024-07-01')) ENGINE = InnoDB)",
        "ALTER TABLE table_name ADD PARTITION (PARTITION p202407 VALUES LESS THAN "
        "(TO_DAYS('2024-08-01')) ENGINE = InnoDB)",
        "ALTER TABLE table_name ADD PARTITION (PARTITION p202408 VALUES LESS THAN "
        "(TO_DAYS('2024-09-01')) ENGINE = InnoDB)",
        "ALTER TABLE table_name ADD PARTITION (PARTITION p202409 VALUES LESS THAN "
        "(TO_DAYS('2024-10-01')) ENGINE = InnoDB)",
        "ALTER TABLE table_name ADD PARTITION (PARTITION p202410 VALUES LESS THAN "
        "(TO_DAYS('2024-11-01')) ENGINE = InnoDB)",
        "ALTER TABLE table_name ADD PARTITION (PARTITION p202411 VALUES LESS THAN "
        "(TO_DAYS('2024-12-01')) ENGINE = InnoDB)",
        "ALTER TABLE table_name ADD PARTITION (PARTITION p202412 VALUES LESS THAN "
        "(TO_DAYS('2025-01-01')) ENGINE = InnoDB)",
        "ALTER TABLE table_name ADD PARTITION (PARTITION p202501 VALUES LESS THAN "
        "(TO_DAYS('2025-02-01')) ENGINE = InnoDB)",
        "ALTER TABLE table_name ADD PARTITION (PARTITION p202502 VALUES LESS THAN "
        "(TO_DAYS('2025-03-01')) ENGINE = InnoDB)",
        "ALTER TABLE table_name ADD PARTITION (PARTITION p202503 VALUES LESS THAN "
        "(TO_DAYS('2025-04-01')) ENGINE = InnoDB)",
        "ALTER TABLE table_name ADD PARTITION (PARTITION p202504 VALUES LESS THAN "
        "(TO_DAYS('2025-05-01')) ENGINE = InnoDB)",
    ]
    assert actual == expect


def test_delete_partition():
    actual = delete_partitions("table_name", dray_run=True)
    expect = "ALTER TABLE table_name DROP PARTITION p202402"
    assert actual == expect
