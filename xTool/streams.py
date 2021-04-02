# -*- coding: utf-8 -*-

"""
来自Python-3.9.2 asyncio/streams.py
"""

import sys
from asyncio import events
from xTool.misc import extract_stack

# 缓冲区的大小：64 KiB
_DEFAULT_LIMIT = 2 ** 16


class IncompleteReadError(EOFError):
    """
    Incomplete read error. Attributes:

    - partial: read bytes string before the end of stream was reached
    - expected: total number of expected bytes (or None if unknown)
    """

    def __init__(self, partial, expected):
        r_expected = 'undefined' if expected is None else repr(expected)
        super().__init__(f'{len(partial)} bytes read on a total of '
                         f'{r_expected} expected bytes')
        self.partial = partial
        self.expected = expected

    def __reduce__(self):
        return type(self), (self.partial, self.expected)


class LimitOverrunError(Exception):
    """Reached the buffer limit while looking for a separator.

    Attributes:
    - consumed: total number of to be consumed bytes.
    """

    def __init__(self, message, consumed):
        super().__init__(message)
        self.consumed = consumed

    def __reduce__(self):
        return type(self), (self.args[0], self.consumed)


class StreamReader:

    _source_traceback = None

    def __init__(self, limit=_DEFAULT_LIMIT, loop=None):
        # The line length limit is  a security feature;
        # it also doubles as half the buffer limit.

        if limit <= 0:
            raise ValueError('Limit cannot be <= 0')

        self._limit = limit
        if loop is None:
            self._loop = events.get_event_loop()
        else:
            self._loop = loop
        self._buffer = bytearray()
        self._eof = False    # Whether we're done.
        self._waiter = None  # A future used by _wait_for_data()
        self._exception = None
        self._transport = None
        self._paused = False
        if self._loop.get_debug():
            self._source_traceback = extract_stack(
                sys._getframe(1))

    def __repr__(self):
        info = ['StreamReader']
        if self._buffer:
            info.append(f'{len(self._buffer)} bytes')
        if self._eof:
            info.append('eof')
        if self._limit != _DEFAULT_LIMIT:
            info.append(f'limit={self._limit}')
        if self._waiter:
            info.append(f'waiter={self._waiter!r}')
        if self._exception:
            info.append(f'exception={self._exception!r}')
        if self._transport:
            info.append(f'transport={self._transport!r}')
        if self._paused:
            info.append('paused')
        return '<{}>'.format(' '.join(info))

    def exception(self):
        """设置future的返回结果 ."""
        return self._exception

    def set_exception(self, exc):
        """将future标为执行完成，并设置Exception ."""
        self._exception = exc

        waiter = self._waiter
        if waiter is not None:
            self._waiter = None
            if not waiter.cancelled():
                waiter.set_exception(exc)

    def _wakeup_waiter(self):
        """Wakeup read*() functions waiting for data or EOF."""
        waiter = self._waiter
        if waiter is not None:
            self._waiter = None
            if not waiter.cancelled():
                waiter.set_result(None)

    def set_transport(self, transport):
        assert self._transport is None, 'Transport already set'
        self._transport = transport

    def _maybe_resume_transport(self):
        if self._paused and len(self._buffer) <= self._limit:
            self._paused = False
            # 恢复接收端。如果有数据可读取时，协议方法 protocol.data_received() 将再次被调用。
            self._transport.resume_reading()

    def feed_eof(self):
        self._eof = True
        self._wakeup_waiter()

    def at_eof(self):
        """Return True if the buffer is empty and 'feed_eof' was called."""
        return self._eof and not self._buffer

    def feed_data(self, data):
        """在内部缓冲区中输入数据字节。将恢复等待数据的任何操作。"""
        assert not self._eof, 'feed_data after feed_eof'

        if not data:
            return

        # 将数据添加到缓冲区
        self._buffer.extend(data)
        # 唤醒生产者消费数据
        self._wakeup_waiter()

        if (self._transport is not None and
                not self._paused and
                len(self._buffer) > 2 * self._limit):
            # 缓冲区过大，停止获取数据
            try:
                self._transport.pause_reading()
            except NotImplementedError:
                # The transport can't be paused.
                # We'll just have to buffer all data.
                # Forget the transport so we don't keep trying.
                self._transport = None
            else:
                self._paused = True

    async def _wait_for_data(self, func_name):
        """Wait until feed_data() or feed_eof() is called.

        If stream was paused, automatically resume it.
        """
        # StreamReader uses a future to link the protocol feed_data() method
        # to a read coroutine. Running two read coroutines at the same time
        # would have an unexpected behaviour. It would not possible to know
        # which coroutine would get the next data.
        if self._waiter is not None:
            raise RuntimeError(
                f'{func_name}() called while another coroutine is '
                f'already waiting for incoming data')
        # 还有剩余数据
        assert not self._eof, '_wait_for_data after EOF'

        # Waiting for data while paused will make deadlock, so prevent it.
        # This is essential for readexactly(n) for case when n > self._limit.
        if self._paused:
            self._paused = False
            # 恢复接收端。如果有数据可读取时，协议方法 protocol.data_received() 将再次被调用。
            self._transport.resume_reading()

        # 等待数据
        self._waiter = self._loop.create_future()
        try:
            await self._waiter
        finally:
            self._waiter = None

    async def readline(self):
        """Read chunk of data from the stream until newline (b'\n') is found.

        On success, return chunk that ends with newline. If only partial
        line can be read due to EOF, return incomplete line without
        terminating newline. When EOF was reached while no bytes read, empty
        bytes object is returned.

        If limit is reached, ValueError will be raised. In that case, if
        newline was found, complete line including newline will be removed
        from internal buffer. Else, internal buffer will be cleared. Limit is
        compared against part of the line without newline.

        If stream was paused, this function will automatically resume it if
        needed.
        """
        sep = b'\n'
        seplen = len(sep)
        try:
            line = await self.readuntil(sep)
        except IncompleteReadError as e:
            # 只获取部分数据
            return e.partial
        except LimitOverrunError as e:
            # 删除溢出的数据
            if self._buffer.startswith(sep, e.consumed):
                del self._buffer[:e.consumed + seplen]
            else:
                self._buffer.clear()
            # 恢复接收端。如果有数据可读取时，协议方法 protocol.data_received() 将再次被调用。
            self._maybe_resume_transport()
            # 抛出异常
            raise ValueError(e.args[0])
        return line

    async def readuntil(self, separator=b'\n'):
        """Read data from the stream until ``separator`` is found.

        On success, the data and separator will be removed from the
        internal buffer (consumed). Returned data will include the
        separator at the end.

        Configured stream limit is used to check result. Limit sets the
        maximal length of data that can be returned, not counting the
        separator.

        If an EOF occurs and the complete separator is still not found,
        an IncompleteReadError exception will be raised, and the internal
        buffer will be reset.  The IncompleteReadError.partial attribute
        may contain the separator partially.

        If the data cannot be read because of over limit, a
        LimitOverrunError exception  will be raised, and the data
        will be left in the internal buffer, so it can be read again.
        """
        seplen = len(separator)
        if seplen == 0:
            raise ValueError('Separator should be at least one-byte string')

        if self._exception is not None:
            raise self._exception

        # Consume whole buffer except last bytes, which length is
        # one less than seplen. Let's check corner cases with
        # separator='SEPARATOR':
        # * we have received almost complete separator (without last
        #   byte). i.e buffer='some textSEPARATO'. In this case we
        #   can safely consume len(separator) - 1 bytes.
        # * last byte of buffer is first byte of separator, i.e.
        #   buffer='abcdefghijklmnopqrS'. We may safely consume
        #   everything except that last byte, but this require to
        #   analyze bytes of buffer that match partial separator.
        #   This is slow and/or require FSM. For this case our
        #   implementation is not optimal, since require rescanning
        #   of data that is known to not belong to separator. In
        #   real world, separator will not be so long to notice
        #   performance problems. Even when reading MIME-encoded
        #   messages :)

        # `offset` is the number of bytes from the beginning of the buffer
        # where there is no occurrence of `separator`.
        offset = 0

        # Loop until we find `separator` in the buffer, exceed the buffer size,
        # or an EOF has happened.
        while True:
            buflen = len(self._buffer)

            # Check if we now have enough data in the buffer for `separator` to
            # fit.
            if buflen - offset >= seplen:
                # 在缓冲区中查找分隔符
                isep = self._buffer.find(separator, offset)

                if isep != -1:
                    # `separator` is in the buffer. `isep` will be used later
                    # to retrieve the data.
                    # 缓冲区中存在分隔符，则停止获取数据
                    break

                # see upper comment for explanation.
                offset = buflen + 1 - seplen
                if offset > self._limit:
                    # 溢出抛出异常，停止进程
                    raise LimitOverrunError(
                        'Separator is not found, and chunk exceed the limit',
                        offset)

            # Complete message (with full separator) may be present in buffer
            # even when EOF flag is set. This may happen when the last chunk
            # adds data which makes separator be found. That's why we check for
            # EOF *ater* inspecting the buffer.
            # 如果终止，只获取部分数据
            if self._eof:
                chunk = bytes(self._buffer)
                self._buffer.clear()
                raise IncompleteReadError(chunk, None)

            # _wait_for_data() will resume reading if stream was paused.
            # 等待数据填充到缓冲区
            await self._wait_for_data('readuntil')

        # 如果缓冲区存在分隔符，但是超出了缓冲区的大小限制
        if isep > self._limit:
            raise LimitOverrunError(
                'Separator is found, but chunk is longer than limit', isep)

        # 获取需要返回的数据（包含分隔符）
        chunk = self._buffer[:isep + seplen]
        del self._buffer[:isep + seplen]
        # 等待数据填充到缓冲区
        self._maybe_resume_transport()
        return bytes(chunk)

    async def read(self, n=-1):
        """Read up to `n` bytes from the stream.

        If n is not provided, or set to -1, read until EOF and return all read
        bytes. If the EOF was received and the internal buffer is empty, return
        an empty bytes object.

        If n is zero, return empty bytes object immediately.

        If n is positive, this function try to read `n` bytes, and may return
        less or equal bytes than requested, but at least one byte. If EOF was
        received before any byte is read, this function returns empty byte
        object.

        Returned value is not limited with limit, configured at stream
        creation.

        If stream was paused, this function will automatically resume it if
        needed.
        """
        # 如果有异常，立即返回
        if self._exception is not None:
            raise self._exception

        # 读取0个字节
        if n == 0:
            return b''

        if n < 0:
            # 读取至EOF标志，并返回读到的所有字节
            # This used to just loop creating a new waiter hoping to
            # collect everything in self._buffer, but that would
            # deadlock if the subprocess sends more than self.limit
            # bytes.  So just call self.read(self._limit) until EOF.
            blocks = []
            while True:
                block = await self.read(self._limit)
                if not block:
                    break
                blocks.append(block)
            return b''.join(blocks)

        # 如果缓冲区为空，且还有剩余数据需要读取
        if not self._buffer and not self._eof:
            # 等待数据放到缓冲区
            await self._wait_for_data('read')

        # 从缓冲区中获取数据，不用担心溢出，是因为bytearray的特性导致的
        # 注意：实际获取的字节数可能小于n，因为缓冲区中数据比较少
        # This will work right even if buffer is less than n bytes
        data = bytes(self._buffer[:n])
        del self._buffer[:n]

        # 恢复接收端。如果有数据可读取时，协议方法 protocol.data_received() 将再次被调用。
        self._maybe_resume_transport()
        return data

    async def readexactly(self, n):
        """Read exactly `n` bytes.

        Raise an IncompleteReadError if EOF is reached before `n` bytes can be
        read. The IncompleteReadError.partial attribute of the exception will
        contain the partial read bytes.

        if n is zero, return empty bytes object.

        Returned value is not limited with limit, configured at stream
        creation.

        If stream was paused, this function will automatically resume it if
        needed.
        """
        if n < 0:
            raise ValueError('readexactly size can not be less than zero')

        if self._exception is not None:
            raise self._exception

        if n == 0:
            return b''

        # 判断缓冲区中数据是否充足
        while len(self._buffer) < n:
            if self._eof:
                incomplete = bytes(self._buffer)
                self._buffer.clear()
                raise IncompleteReadError(incomplete, n)
            # 等待数据进入缓冲区
            await self._wait_for_data('readexactly')

        if len(self._buffer) == n:
            data = bytes(self._buffer)
            self._buffer.clear()
        else:
            data = bytes(self._buffer[:n])
            del self._buffer[:n]
        self._maybe_resume_transport()
        return data

    def __aiter__(self):
        return self

    async def __anext__(self):
        val = await self.readline()
        if val == b'':
            raise StopAsyncIteration
        return val
