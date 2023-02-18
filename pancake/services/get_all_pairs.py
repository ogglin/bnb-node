import asyncio
import datetime

from pancake import *
from db import async_query

insert_count = 0
finenum = 175
sql_insert = ''


async def add_pool(pool_id, pool_contract, token0_contract, token0_name, token0_symbol, token0_decimals,
                   token1_contract, token1_name, token1_symbol, token1_decimals):
    global sql_insert, insert_count, finenum
    token0_symbol = token0_symbol.replace("'", "''")
    token0_name = token0_name.replace("'", "''")
    token1_symbol = token1_symbol.replace("'", "''")
    token1_name = token1_name.replace("'", "''")
    if insert_count > 3000:
        file = open(f'pancake_sql{finenum}.sql', 'w')
        file.write(sql_insert)
        file.close()
        # _query(sql_insert)
        finenum += 1
        insert_count = 0
        print(f'pancake_sql{finenum}.sql', datetime.datetime.now())
    else:
        q = f"""insert into pools_pancake (id, pool_contract, token0_contract, token0_symbol, token0_decimals, token0_name,
         token1_contract, token1_symbol, token1_decimals, token1_name, is_active)
        VALUES({pool_id},'{pool_contract}', '{token0_contract}', '{token0_symbol}', '{token0_decimals}', '{token0_name}',
               '{token1_contract}', '{token1_symbol}', '{token1_decimals}', '{token1_name}', true) ON CONFLICT (id) DO NOTHING;
               """
        sql_insert += q
        insert_count += 1


async def get_token_info(addr):
    address = Web3.toChecksumAddress(addr)
    token_factory = w3http.eth.contract(address=address, abi=ABIPoolPancake)
    token_name = token_factory.functions.name().call()
    token_symbol = token_factory.functions.symbol().call()
    token_decimals = token_factory.functions.decimals().call()
    return token_name, token_symbol, token_decimals


async def get_pool_info(addr):
    address = Web3.toChecksumAddress(addr)
    pool_factory = w3http.eth.contract(address=address, abi=ABIPoolPancake)
    symbol = pool_factory.functions.symbol().call()
    token0_contract = pool_factory.functions.token0().call()
    token0_name, token0_symbol, token0_decimals = await get_token_info(token0_contract)
    token1_contract = pool_factory.functions.token1().call()
    token1_name, token1_symbol, token1_decimals = await get_token_info(token1_contract)
    return token0_contract, token0_name, token0_symbol, token0_decimals, token1_contract, token1_name, token1_symbol, token1_decimals


async def get_pool(pool_id):
    print(pool_id)
    pool_contract = pancake_factory.functions.allPairs(pool_id).call()
    try:
        token0_contract, token0_name, token0_symbol, token0_decimals, token1_contract, token1_name, token1_symbol, token1_decimals = await get_pool_info(
            pool_contract)
        await add_pool(pool_id, pool_contract, token0_contract, token0_name, token0_symbol, token0_decimals,
                       token1_contract, token1_name, token1_symbol, token1_decimals)
    except Exception as err:
        print('error:', err, pool_id, pool_contract)


async def run():
    # pools_n = (_query("select id from pools_pancake order by id DESC limit 1;"))[0][0]
    pools_n = 536996
    pools_count = pancake_factory.functions.allPairsLength().call()
    print(pools_count)
    pool_id = pools_n + 1
    bath_tasks = []
    while pool_id < pools_count:
        await get_pool(pool_id)
        pool_id += 1
        # for i in range(100):
        #     bath_tasks.append(get_pool(pool_id))
        #     pool_id += 1
        # await asyncio.gather(*bath_tasks)
        # print('bath_tasks done', pools_count - pool_id)


# run()
if __name__ == '__main__':
    asyncio.run(run())
