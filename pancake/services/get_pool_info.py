import asyncio
import json
import time

from aiomultiprocess import Pool

from db import redis, sync_query
from pancake import *
from pancake.services import stable_pools

polls_stable = {}


async def get_gap_bnb(gap=2000):
    global polls_stable
    pool = polls_stable['USDT_WBNB'][0]
    x = pool['reserves'][0] / 10 ** int(pool['token0_decimals'])
    y = pool['reserves'][1] / 10 ** int(pool['token1_decimals'])
    gap_bnb = x * y / (x - gap * (1 + 0.003)) - y
    return gap_bnb


async def check_liquid(pool, gap_bnb, gap=1000):
    if pool['token0_symbol'] == 'WBNB':
        if gap_bnb < pool['reserves'][0] / 10 ** int(pool['token0_decimals']):
            return True
    if pool['token1_symbol'] == 'WBNB':
        if gap_bnb < pool['reserves'][1] / 10 ** int(pool['token1_decimals']):
            return True
    if pool['token0_symbol'] == 'USDT' or pool['token0_symbol'] == 'BUSD' or pool['token0_symbol'] == 'USDC':
        if gap < pool['reserves'][0] / 10 ** int(pool['token0_decimals']):
            return True
    if pool['token1_symbol'] == 'USDT' or pool['token1_symbol'] == 'BUSD' or pool['token1_symbol'] == 'USDC':
        if gap < pool['reserves'][1] / 10 ** int(pool['token1_decimals']):
            return True
    return False


async def set_pools():
    pools = await sync_query(f"""select pancake_pools.*
        from pancake_pools left join trusted_tokens_bsc ttb 
        on (pancake_pools.token0_contract = ttb.contract or pancake_pools.token1_contract = ttb.contract)
        where ttb.is_active = true or ttb.strong_active = true;""")
    jpools = []
    for pool in pools:
        jpools.append(list(pool))
    await redis.hdel('pools', 'pancake')
    await redis.hset('pools', 'pancake', json.dumps(jpools))


async def get_pools():
    return json.loads(await redis.hget('pools', 'pancake'))


async def get_pool_info(pool):
    pool_contract, token0_contract, token0_symbol, token0_decimals, token1_contract, token1_symbol, token1_decimals, tsymbol, strong_active = pool
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
        "key": token0_symbol + '_' + token1_symbol,
        "pool_contract": pool_contract,
        "strong_active": strong_active
    }
    return pool_info


async def get_pools_from_node(pools):
    result_pools = []
    async with Pool(processes=10) as pool:
        async for result in pool.map(get_pool_info, pools):
            result_pools.append(result)
    return result_pools


async def get_ready_pools(pools):
    ready_pools = {}
    pool_infos = await get_pools_from_node(pools)
    for pool_info in pool_infos:
        if pool_info['key'] not in ready_pools:
            ready_pools[pool_info['key']] = []
        ready_pools[pool_info['key']].append(pool_info)
    return ready_pools


async def start():
    global polls_stable
    print('run_pools start')
    tstart = time.time()
    try:
        pools = await get_pools()
    except Exception as err:
        await set_pools()
        pools = await get_pools()
    print(len(pools))
    all_pools = {}
    polls_stable = await get_ready_pools(stable_pools)
    gap_bnb = await get_gap_bnb()
    ready_pools = await get_ready_pools(pools)
    for key, item in polls_stable.items():
        all_pools[key] = json.dumps(item)
    for key, item in ready_pools.items():
        # liq = await check_liquid(item[0], gap_bnb)
        # if liq:
        all_pools[key] = json.dumps(item)
    print(len(all_pools))
    await redis.hset('pools_pancake', mapping=all_pools)
    print('run_pools done!', time.time() - tstart)


async def run_pools():
    while True:
        try:
            await start()
        except Exception as err:
            print('try run_pools', err)


async def main():
    await start()


if __name__ == '__main__':
    asyncio.run(main())
