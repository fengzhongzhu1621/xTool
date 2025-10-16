from inspect import isawaitable


def trigger_events(events, loop):
    """Trigger event callbacks (functions or async)

    :param events: one or more sync or async functions to execute
    :param loop: event loop
    """
    for event in events:
        # 执行事件处理器
        result = event(loop)
        if isawaitable(result):
            # 一直运行直到future运行完成
            loop.run_until_complete(result)
