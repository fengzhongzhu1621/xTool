#!python
# cython: language_level=3, boundscheck=False, wraparound=False

from libcpp.queue cimport queue

from cpython.ref cimport PyObject


ctypedef unsigned short ushort
ctypedef unsigned int uint
ctypedef unsigned long ulong


# 引入C++ mutext
# Mutex 又称互斥量，
# C++ 11中与 Mutex 相关的类（包括锁类型）和函数都声明在 <mutex> 头文件中，所以如果你需要使用 std::mutex，就必须包含 <mutex> 头文件。
# lock_guard:
#   * 是采用RAII手法封装的一个类，功能与mutex一样 其在构造时自动对mutex进行锁定（lock），
#   * 在析构时，在析构函数中自动对mutex进行解锁（unlock）
# 递归锁（recursive_mutex）:
#   * 允许同一线程多次锁定，并在最近一次相应的unlock时释放lock
#   * 调用方线程在从它成功调用 lock 或 try_lock 开始的时期里占有 recursive_mutex 。此时期间，调用方线程可以多次锁定/解锁互斥元。结束的时候lock与unlock次数匹配正确就行。
#   * 线程占有 recursive_mutex 时，若其他所有线程试图要求 recursive_mutex 的所有权，则它们将阻塞（对于调用 lock ）或收到 false 返回值（对于调用 try_lock ）。
#   * 可锁定 recursive_mutex 次数的最大值是未指定的，但抵达该数后，对 lock 的调用将抛出 std::system_error 而对 try_lock 的调用将返回 false 。
#   * 例子： std::lock_guard<std::recursive_mutex> lk(m);
cdef extern from "<mutex>" namespace "std" nogil:
    cdef cppclass recursive_mutex:
        pass

    cdef cppclass lock_guard[T]:
        lock_guard(recursive_mutex rm)


cdef class CythonDemo:
    cdef:
        public object object_a
        int int_a
        char char_a[16]
        bint b_int_a

    cpdef str action_strcpy(self)
