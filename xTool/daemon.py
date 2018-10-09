# -*- coding: utf-8 -*-

import sys
import os
import time
import atexit
from signal import SIGTERM


class Daemon(object):
    """
    A generic daemon class.
   
    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.daemon_stdin = stdin
        self.daemon_stdout = stdout
        self.daemon_stderr = stderr
        self.pidfile = pidfile
   
    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        # ----------------------------------------------------------------------
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # ----------------------------------------------------------------------
        # decouple from parent environment
        # 进程活动时，其工作目录所在的文件系统不能卸下。以免影响可加载文件系统。
        # 避免有任何目录因为还有 process 在路径内, 使得目录已被移除, 却无法释放空间。
        os.chdir("/")
        # ----------------------------------------------------------------------
        # 调用setsid创建一个新的session，使自己成为新session和新进程组的leader，并使进程没有控制终端(tty)。
        # 成功调用该函数的结果是：
        #   创建一个新的Session，当前进程成为Session Leader，当前进程的id就是Session的id。
        #   创建一个新的进程组，当前进程成为进程组的Leader，当前进程的id就是进程组的id。
        #   如果当前进程原本有一个控制终端，则它失去这个控制终端，成为一个没有控制终端的进程。所谓失去控制终端是指，原来的控制终端仍然是打开的，仍然可以读写，但只是一个普通的打开文件而不是控制终端了。
        os.setsid()
        # ----------------------------------------------------------------------
        # 进程从创建它的父进程那里继承了文件创建掩模。它可能修改守护进程所创建的文件的存取位。为防止这一点，将文件创建掩模清除
        # 避免创建文件时权限的影响。
        os.umask(0)

        # ----------------------------------------------------------------------
        # do second fork
        # 此时子进程仍是 session leader, 有机会开启新的 terminal。若要避免这种可能, 再调用一次 fork(), 并让原本的 parent process 离开, 
        # 这样 daemon process 就会处在一个没有 terminal 也没有 session leader 的情况, 会更安全。
        # session leader调用新terminal的情况
        #   * 基于System V的Unix系统会为打开一个还未分配到任何session的终端设备，把它当作controlling terminal来使用 
        #       System V在调用open时，如果没有指定0_NOCTTY这个flag就会这样 
        #   * 基于BSD的Unix系统会在session leader调用ioctl时带上TIOCSCTTY参数，分配一个controlling terminal；
        #     而如果调用时该进程恰巧已经有一个controlling terminal，则调用会失败，所以一般来紧跟一个setsid()来保证调用的正确。然后在POSIX.1规范中，BSD系统并不会使用上面提到的0_NOCTTY这样的参数 
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # ----------------------------------------------------------------------
        # redirect standard file descriptors
        # 将sys.stdin, sys.stdout, sys.stderr默认重定向到/dev/null
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.daemon_stdin, 'r')
        so = open(self.daemon_stdout, 'a+')
        se = open(self.daemon_stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # ----------------------------------------------------------------------
        #  通过pid文件，确定守护进程的唯一性
        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        open(self.pidfile, 'w+').write("%s\n" % pid)
   
    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart
        # Try killing the daemon process       
        try:
            while 1:
                # 当第二次杀死daemon时，因为此进程已经不存在，则抛出OSError异常
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err))
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """

 
if __name__ == "__main__":
    import sys
    import time
     
    class MyDaemon(Daemon):
        def run(self):
            while True:
                time.sleep(1)

    daemon = MyDaemon('/tmp/daemon-example.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
