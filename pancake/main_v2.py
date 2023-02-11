import asyncio
import json
import os

from datetime import datetime, timezone
from aiomultiprocess import Pool
from web3 import Web3

from pancake import *
from pancake.services.db import _query
from db_redis_async import redis, redis_rs

is_test = False


async def check_liquid(usd_cur, btc_cur, pool_info):
    pool = list(pool_info.items())[0][1]
    trashhold = 2000
    # print('/********', pool[6])
    isCheck = False
    if pool[3][0] == 'USDC' or pool[3][0] == 'USDT' or pool[3][0] == 'DAI':
        if trashhold < pool[0][0] / 10 ** int(pool[3][1]):
            return True
    if pool[4][0] == 'USDC' or pool[4][0] == 'USDT' or pool[4][0] == 'DAI':
        if trashhold < pool[0][1] / 10 ** int(pool[4][1]):
            return True
    if pool[3][0] == 'WETH':
        if trashhold / usd_cur < pool[0][0] / 10 ** int(pool[3][1]):
            return True
    if pool[4][0] == 'WETH':
        if trashhold / usd_cur < pool[0][1] / 10 ** int(pool[4][1]):
            return True
    if pool[3][0] == 'WBTC':
        if trashhold / usd_cur * btc_cur < pool[0][0] / 10 ** int(pool[3][1]):
            return True
    if pool[4][0] == 'WBTC':
        if trashhold / usd_cur * btc_cur < pool[0][1] / 10 ** int(pool[4][1]):
            return True
    return isCheck


async def get_price(pair):
    reservs, contract0, contract1, token0, token1, stable = pair
    x = float(reservs[0]) / 10 ** token0[1]
    y = float(reservs[1]) / 10 ** token1[1]
    price_token = 0
    if x > 1 and y > 1:
        if token0[0] == stable:
            price_token = x * y / (y - 1) - x


def get_token_info(addr):
    address = Web3.toChecksumAddress(addr)
    token_factory = w3http.eth.contract(address=address, abi=ABIPoolPancake)
    try:
        symbol = token_factory.functions.symbol().call()
    except:
        symbol = str(addr)
    try:
        decimals = token_factory.functions.decimals().call()
    except:
        decimals = 18
    return symbol, decimals


async def get_node_token(addr):
    address = Web3.toChecksumAddress(addr)
    pool_factory = w3http.eth.contract(address=address, abi=ABIPoolPancake)
    reservs = pool_factory.functions.getReserves().call()
    contract0 = pool_factory.functions.token0().call()
    contract1 = pool_factory.functions.token1().call()
    token0 = get_token_info(contract0)
    token1 = get_token_info(contract1)
    await asyncio.sleep(0)
    return reservs, contract0, contract1, token0, token1


async def get_pool(pool):
    try:
        stime = datetime.now()
        pool_contract, token0_contract, token0_symbol, token0_decimals, token1_contract, token1_symbol, token1_decimals, tsymbol, strong_active = pool
        pool_info = await get_node_token(pool_contract)
        if token0_symbol.lower() in tsymbol.lower() or tsymbol.lower() in token0_symbol.lower():
            if is_test:
                print('Get pool:', datetime.now() - stime)
            return {token0_symbol + '_' + token1_symbol: pool_info + (
                token1_symbol, pool_contract, tsymbol, 'uni_v2', strong_active)}
        elif token1_symbol.lower() in tsymbol.lower() or tsymbol.lower() in token1_symbol.lower():
            if is_test:
                print('Get pool:', datetime.now() - stime)
            return {token0_symbol + '_' + token1_symbol: pool_info + (
                token0_symbol, pool_contract, tsymbol, 'uni_v2', strong_active)}
        else:
            if 'WETH' in token0_symbol or 'WETH' in token1_symbol:
                if is_test:
                    print('Get pool:', datetime.now() - stime)
                return {token0_symbol + '_' + token1_symbol: pool_info + (
                    'WETH', pool_contract, tsymbol, 'uni_v2', strong_active)}
            elif 'DAI' in token0_symbol or 'DAI' in token1_symbol:
                if is_test:
                    print('Get pool:', datetime.now() - stime)
                return {token0_symbol + '_' + token1_symbol: pool_info + (
                    'DAI', pool_contract, tsymbol, 'uni_v2', strong_active)}
            elif 'USDT' in token0_symbol or 'USDT' in token1_symbol:
                if is_test:
                    print('Get pool:', datetime.now() - stime)
                return {token0_symbol + '_' + token1_symbol: pool_info + (
                    'USDT', pool_contract, tsymbol, 'uni_v2', strong_active)}
            elif 'USDC' in token0_symbol or 'USDC' in token1_symbol:
                if is_test:
                    print('Get pool:', datetime.now() - stime)
                return {token0_symbol + '_' + token1_symbol: pool_info + (
                    'USDC', pool_contract, tsymbol, 'uni_v2', strong_active)}
            elif 'WBTC' in token0_symbol or 'WBTC' in token1_symbol:
                if is_test:
                    print('Get pool:', datetime.now() - stime)
                return {token0_symbol + '_' + token1_symbol: pool_info + (
                    'WBTC', pool_contract, tsymbol, 'uni_v2', strong_active)}
            else:
                if is_test:
                    print('Get pool:', datetime.now() - stime)
                return {token0_symbol + '_' + token1_symbol: pool_info + (
                    tsymbol, pool_contract, tsymbol, 'uni_v2', strong_active)}
    except Exception as err:
        if is_test:
            print('get_pool err:', err)
        else:
            pass


async def init_pools():
    pools_pancake = None
    settings = None
    start = datetime.now()

    # while True:
    results = {}
    while settings is None:
        try:
            settings = json.loads(await redis_rs.get('settings'))
        except:
            pass
    usd_cur = settings['currency_usd']
    btc_cur = settings['currency']
    while pools_pancake is None:
        try:
            pools_pancake = json.loads(await redis_rs.get('pools-pancake'))
        except:
            pass
    print(len(pools_pancake))
    async with Pool() as pool:
        async for result in pool.map(get_pool, pools_pancake):
            if result:
                if list(result.items())[0][1][9] is True:
                    key = list(result.keys())[0]
                    results[key] = str(result[key]).replace("(", "[").replace(")", ']').replace("'", '"')
                elif await check_liquid(usd_cur, btc_cur, result):
                    key = list(result.keys())[0]
                    results[key] = str(result[key]).replace("(", "[").replace(")", ']').replace("'", '"')
    # await init_prices()
    print('results', len(results))
    # for result in results:
    #     for k, v in result.items():
    print('Estimate pools-pancake time: ', str(datetime.now() - start))
    start = datetime.now()
    await redis.delete('pools-pancake')
    await redis.hset('pools-pancake', mapping=results)
    await redis.hset('timers', 'pancake', str(datetime.now(timezone.utc)))
    print('set pools-pancake to db time: ', str(datetime.now() - start))
    # except Exception as err:
    #     print(err)
    # os.system('nohup /opt/eth_node.sh &')


async def start_pool_v2():
    try:
        print('Start pools v2 tokens')
        start = datetime.now()
        await init_pools()
        print('set pool_v2', datetime.now() - start)
    except Exception as err:
        print('Error:', err)


async def main():
    if is_test:
        await start_pool_v2()
    else:
        while True:
            try:
                await start_pool_v2()
            except Exception as err:
                print(err)


if __name__ == '__main__':
    asyncio.run(main())
