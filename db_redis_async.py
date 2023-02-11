import json

import aioredis

redis_url = "redis://65.21.191.118"
redis_url_rs = "redis://135.181.196.183"
dbNum = 0
dbNumTest = 1
password = '$QLX2lE8Zin13i9XyI6A1W!VSVA7rA'

redis = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True, db=dbNum,
                          password=password
                          )

redis_rs = aioredis.from_url(redis_url_rs, decode_responses=True, db=dbNum, password=password)


async def hscan(hashkey, key):
    return await redis.hscan(hashkey, 0, '*' + key + '*', 5000)


async def insert_by_key(key, value):
    async with redis.client() as conn:
        await conn.set(key, json.dumps(value))


async def zadd(key, data):
    await redis.zadd(key, data)


async def sadd(key, data):
    await redis.sadd(key, data)


async def smembers(key):
    return await redis.smembers(key)


async def zrange(key, start, end):
    return await redis.zrange(key, start, end)


async def hget(hashkey, subkey):
    return await redis.hget(hashkey, subkey)


async def hset(hashkey, subkey, data):
    return await redis.hset(hashkey, subkey, data)


async def hdel(hashkey, subkey):
    return await redis.hdel(hashkey, subkey)


async def select_by_key(key):
    async with redis.client() as conn:
        return await conn.get(key)


async def delete(keys):
    for key in keys:
        await redis.delete(key)


async def select_key(numDB, key):
    async with redis.client() as conn:
        return await conn.get(key)


async def insert_key(numDB, key, value):
    async with redis.client() as conn:
        await conn.set(key, json.dumps(value))
