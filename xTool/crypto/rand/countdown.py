import math
import random

__all__ = [
    "calculate_countdown_use_mod",
    "calculate_countdown_use_random",
    "calculate_countdown",
]


def calculate_countdown_use_mod(count: int, index: int, duration: int) -> int:
    """
    周期性任务均匀分布到执行周期内，通过取模和随机分配实现削峰。

    :param count: 任务总数
    :param index: 当前任务索引（从0开始）
    :param duration: 执行周期总时长（秒）
    :return: 当前任务的执行倒计时时间（秒）
    """
    # 确保duration >= count，否则任务间隔过小
    if duration < count:
        raise ValueError("Duration must be greater than or equal to the number of tasks.")

    # 计算单位时间间隔，确保至少为1分钟
    # 将理想间隔时间向上取整，确保每个任务至少有一个时间单位。
    # 计算每个任务的理想间隔时间
    unit_per_task = max(math.ceil(duration / count), 60)

    # 计算当前任务所在的时间区间位置 pos:
    interval_count = math.ceil(duration / unit_per_task)  # 总区间数
    pos = index % interval_count

    # 计算当前区间的起始和结束时间
    start_time = pos * unit_per_task
    end_time = min((pos + 1) * unit_per_task - 1, duration)  # 确保不超出总duration

    # 在当前时间区间内随机选择一个时间点作为任务的执行时间
    return random.randint(start_time, end_time)


def calculate_countdown_use_random(duration: int) -> int:
    """
    把周期任务通过随机数的方式平均分布到 duration 秒 内执行，用于削峰

    :param duration: 执行周期总时长（秒）
    :return: 当前任务的执行倒计时时间（秒）
    """
    return random.randint(0, max(duration - 1, 1))


def calculate_countdown(count: int, index: int, duration: int) -> int:
    """
    把周期任务随机平均分布到 duration 秒内执行，用于削峰

    :param count: 任务总数
    :param index: 当前任务索引（从0开始）
    :param duration: 执行周期总时长（秒）
    :return: 当前任务的执行倒计时时间（秒）
    """
    # 任务总数小于等于1时立即执行
    if count <= 1:
        return 0
    funcs = [calculate_countdown_use_mod, calculate_countdown_use_random]
    return funcs[random.randint(0, 1)](count=count, index=index, duration=duration)
