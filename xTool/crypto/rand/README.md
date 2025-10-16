# 随机数生成器

* 随机数生成器 （RNG, random number generator）
* 伪随机数生成器（PRNG, pseudo-random number generator）
这些随机数主要通过一个固定的、可重复的计算方法生成，计算方法经过特殊的设计，产生的结果具有类似真随机数的统计学特征。一般只是重复的周期比较大的数列，以算法和种子值共同作用生成。
* 密码学伪随机数生成器（CPRNG, cryptographic pseudo-random number generator） 能够生成密码学安全随机数
* 强伪随机数CSPRNG（安全可靠的伪随机数生成器(Cryptographically Secure Pseudo-Random Number Generator））

# 非物理真随机数产生器
* Linux /dev/random设备接口（存在阻塞问题）
```
/dev/random 阻塞
/dev/urandom 非阻塞
```
/dev/urandom 的输出不来自于熵池，而是直接从 CSPRNG 来。
在系统熵池耗尽之前，/dev/random 和 /dev/urandom在安全性上是一致的。
即使熵池耗尽，CSPRNG的种子也是真正的随机数，产生的随机数也足够安全。

* Windows CryptGenRandom() 接口

# 安全随机数
* 随机数要足够长，避免暴力破解
* 不同用处的随机数使用不同的种子
* 对安全性要求高的随机数（如密码技术相关）禁止使用的弱伪随机数

# 弱随机数方案
```python
import time
import numpy

rng = numpy.random.RandomState( time() )
array_rand_num = rng.uniform()
```

```python
import random
random.seed()
```

# 强伪随机数方案
```python
import os

os.urandom
```

