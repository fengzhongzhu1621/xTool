from asgiref.sync import SyncToAsync
from django.db import close_old_connections

# SyncToAsync 是 asgiref 库中的一个实用工具类，用于将同步函数转换为异步函数。这在处理需要在异步上下文中执行的同步代码时非常有用。
# SyncToAsync 包装器允许你以异步方式调用同步函数，同时确保它们在适当的线程上执行，以避免阻塞事件循环。


class DatabaseSyncToAsync(SyncToAsync):
    """
    SyncToAsync version that cleans up old database connections when it exits.
    """

    def thread_handler(self, loop, *args, **kwargs):
        # django.db.close_old_connections 是 Django 中的一个实用函数，
        # 用于关闭数据库连接池中所有超过其最大生命周期（CONN_MAX_AGE 设置）的连接。
        # 这个函数在 Django 内部自动调用，以确保数据库连接得到正确的管理和资源释放。
        #
        # CONN_MAX_AGE 是一个 Django 设置，用于控制数据库连接的最大生命周期。
        # 当 CONN_MAX_AGE 设置为非零值时，Django 会尝试重用旧连接，而不是为每个请求创建新连接。
        # 这可以提高性能，减少数据库服务器的负担。然而，长时间保持打开的连接可能会导致资源泄漏和其他问题。
        #
        # close_old_connections 函数通过遍历数据库连接池并检查每个连接的最后使用时间来实现。
        # 如果连接的最后使用时间超过了 CONN_MAX_AGE，则会关闭该连接。
        close_old_connections()
        try:
            return super().thread_handler(loop, *args, **kwargs)
        finally:
            close_old_connections()


# The class is TitleCased, but we want to encourage use as a callable/decorator
database_sync_to_async = DatabaseSyncToAsync
