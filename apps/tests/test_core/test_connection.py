from apps.core.connection import print_sql_execute_result


def test_print_sql_execute_result():
    print_sql_execute_result("default", "show tables")
