"""
Locking constants

Lock types:

- `LOCK_EX` exclusive lock
- `LOCK_SH` shared lock

Lock flags:

- `LOCK_NB` non-blocking

Manually unlock, only needed internally

- `LOCK_UN` unlock

“文件锁”-flock: 建议性锁，不具备强制性。
一个进程使用flock将文件锁住，另一个进程可以直接操作正在被锁的文件，修改文件中的数据，
原因在于flock只是用于检测文件是否被加锁，针对文件已经被加锁，另一个进程写入数据的情况，内核不会阻止这个进程的写入操作，也就是建议性锁的内核处理策略。

flock主要三种操作类型：
LOCK_SH，共享锁，多个进程可以使用同一把锁，常被用作读共享锁；如果是读取，不需要等待，但如果是写入，需要等待读取完成
LOCK_EX，排他锁，同时只允许一个进程使用，常被用作写锁；无论写入/读取都需要等待
LOCK_UN，释放锁；无论使用共享/排他锁，使用完后需要解锁

进程使用flock尝试锁文件时，如果文件已经被其他进程锁住，进程会被阻塞直到锁被释放掉，
LOCK_NB，在尝试锁住该文件的时候，不阻塞而是提示锁定，发现已经被其他服务锁住，会返回错误，errno错误码为EWOULDBLOCK。(不支持windows)

"""

import os

# The actual tests will execute the code anyhow so the following code can
# safely be ignored from the coverage tests
if os.name == "nt":  # pragma: no cover
    import msvcrt

    LOCK_EX = 0x1  #: exclusive lock
    LOCK_SH = 0x2  #: shared lock
    LOCK_NB = 0x4  #: non-blocking
    LOCK_UN = msvcrt.LK_UNLCK  #: unlock

elif os.name == "posix":  # pragma: no cover
    import fcntl

    # 排他锁，同时只允许一个进程使用，常被用作写锁
    LOCK_EX = fcntl.LOCK_EX  #: exclusive lock
    # 共享锁，多个进程可以使用同一把锁，常被用作读共享锁
    LOCK_SH = fcntl.LOCK_SH  #: shared lock
    LOCK_NB = fcntl.LOCK_NB  #: non-blocking
    LOCK_UN = fcntl.LOCK_UN  #: unlock

else:  # pragma: no cover
    raise RuntimeError("Locker only defined for nt and posix platforms")
