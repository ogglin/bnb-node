import asyncio
import json
import time

from aiomultiprocess import Pool

from db_redis_async import redis_rs
from pancake import *
from pancake.services.db import _query


async def set_pools():
    pools = _query("""select pool_contract, token0_contract, token0_symbol, token0_decimals, token1_contract, token1_symbol, token1_decimals
                    from pools_pancake where is_active = true limit 1000;""")
    await redis_rs.hset('pools', 'pancake', json.dumps(pools))


async def get_pools():
    return json.loads(await redis_rs.hget('pools', 'pancake'))


async def get_pool_info(pool):
    pool_contract, token0_contract, token0_symbol, token0_decimals, token1_contract, token1_symbol, token1_decimals = pool
    address = Web3.toChecksumAddress(pool_contract)
    pool_factory = w3http.eth.contract(address=address, abi=ABIPoolPancake)
    reserves = pool_factory.functions.getReserves().call()
    tsymbol = token0_symbol
    if token0_symbol == 'WBNB':
        tsymbol = token1_symbol
    pool_info = {
        "reserves": reserves,
        "token0_contract": token0_contract,
        'token0_symbol': token0_symbol,
        'token0_decimals': token0_decimals,
        "token1_contract": token1_contract,
        'token1_symbol': token1_symbol,
        'token1_decimals': token1_decimals,
        "tsymbol": tsymbol,
        "amm": "pancake",
        "strong_active": True,
        "key": token0_symbol + '_' + token1_symbol,
        "pool_contract": pool_contract
    }
    return pool_info


async def get_pools_from_node(pools):
    pstart = time.time()
    result_pools = []
    async with Pool() as pool:
        async for result in pool.map(get_pool_info, pools):
            result_pools.append(result)
    print('get_pools_from_node', time.time() - pstart)
    return result_pools


async def main():
    # await set_pools()
    tstart = time.time()
    pools = await get_pools()
    ready_pools = {}
    pool_infos = await get_pools_from_node(pools)
    for pool_info in pool_infos:
        if pool_info['key'] not in ready_pools:
            ready_pools[pool_info['key']] = []
        ready_pools[pool_info['key']].append(pool_info)
    for key, item in ready_pools.items():
        ready_pools[key] = json.dumps(item)
    await redis_rs.hset('pools_pancake', mapping=ready_pools)
    print('done!', time.time() - tstart)


if __name__ == '__main__':
    asyncio.run(main())
