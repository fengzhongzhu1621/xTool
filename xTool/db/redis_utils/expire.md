# Redis 是如何判断数据是否过期

通过一个过期字典来保存数据过期的时间。过期字典的键指向 Redis 数据库中的某个 key(键)，
过期字典的值是一个 long long 类型的整数，保存了 key 所指向的数据库键的过期时间（毫秒精度的 UNIX 时间戳）。

```
typedef struct redisDb {
    ...

    dict *dict;     //数据库键空间,保存着数据库中所有键值对
    dict *expires   // 过期字典,保存着键的过期时间
    ...
} redisDb;
```

在查询一个 key 的时候，Redis 首先检查 key 是否存在于过期字典 expires 中（时间复杂度为 O(1)），
如果不在就直接返回，存在则需要判断 key 是否过期，过期直接删除 key 然后返回 null

# Redis 过期 key 删除策略

## 1. 惰性删除
只会在取出/查询 key 的时候才对数据进行过期检查。对 CPU 最友好，但会造成太多过期 key 没有被删除。


## 2. 定期删除
周期性地随机从设置了过期时间的 key 中抽查一批，然后逐个检查这些 key 是否过期，
过期就删除 key。并不保证所有过期键都会被立即删除。相比于惰性删除，对内存更友好，对 CPU 不太友好。

不把所有过期 key 都删除，是为了平衡内存和性能。

定期删除还会受到执行时间和过期 key 的比例的影响
* 执行时间已超过阈值（即执行超时），会中断当前的定期删除循环，以避免使用过多的 CPU 时间。
* 如果这一批过期的 key 比例超过一个比例，就会重复下一轮的删除流程，以更积极地清理过期 key。
相应地； 如果过期的 key 比例低于这个比例， 就会中断这一次定期删除循环，避免做过多的工作而获得很少的内存回收。

```
// 定义了一个快速扫描周期的持续时间，单位是微秒。在这个时间内，Redis会尝试扫描尽可能多的键，以便尽快发现过期的键。
#define ACTIVE_EXPIRE_CYCLE_FAST_DURATION 1000 /* Microseconds. */
// 定义了慢速扫描周期中允许使用的最大CPU百分比。当Redis在慢速扫描周期中花费的时间超过这个百分比时，
// 它会减少扫描速度，以避免对其他操作产生过多影响。
#define ACTIVE_EXPIRE_CYCLE_SLOW_TIME_PERC 25 /* Max % of CPU to use. */
// 定义了可接受的陈旧键的百分比。当Redis发现超过这个百分比的键已经过期但尚未被删除时，
// 它会增加扫描频率和额外努力来清除这些陈旧键。
#define ACTIVE_EXPIRE_CYCLE_ACCEPTABLE_STALE 10 /* % of stale keys after which
                                                   we do extra efforts. */
```
### 2.1 每次随机抽查数量是多少？

```
// 表示在每次遍历数据库时，Redis将尝试处理20个键。
// 这个值可以根据实际需求进行调整。较大的值可能会导致更快的过期键清理，但也可能增加CPU使用率。
// 较小的值可能会降低CPU使用率，但可能导致过期键清理速度较慢。
#define ACTIVE_EXPIRE_CYCLE_KEYS_PER_LOOP 20 /* Keys for each DB loop. */
```

### 2.2 如何控制定期删除的执行频率？

定期删除的频率是由 hz 参数控制的。
hz 默认为 10，代表每秒执行 10 次，也就是每秒钟进行 10 次尝试来查找并删除过期的 key。

hz 的取值范围为 1~500。
增大 hz 参数的值会提升定期删除的频率。如果你想要更频繁地执行定期删除任务，可以适当增加 hz 的值，但这会加 CPU 的使用率。
根据 Redis 官方建议，hz 的值不建议超过 100，对于大部分用户使用默认的 10 就足够了。

dynamic-hz 这个参数开启之后 Redis 就会在 hz 的基础上动态计算一个值。Redis 提供并默认启用了使用自适应 hz 值的能力，

```
# 默认为 10
hz 10
# 默认开启
dynamic-hz yes
```

### 2.3 大量 key 集中过期怎么办？

* 尽量避免 key 集中过期，在设置键的过期时间时尽量随机一点。
* 对过期的 key 开启 lazyfree 机制（修改 redis.conf 中的 lazyfree-lazy-expire 参数），
会在后台异步删除过期的 key，不会阻塞主线程的运行。