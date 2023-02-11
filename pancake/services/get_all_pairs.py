import asyncio
from pancake import *
from pancake.services.db import _query

insert_count = 0
sql_insert = ''


def add_pool(pool_id, pool_contract, token0_contract, token0_name, token0_symbol, token0_decimals,
             token1_contract, token1_name, token1_symbol, token1_decimals):
    global sql_insert, insert_count
    token0_name = token0_name.replace("'", '"')
    token1_name = token1_name.replace("'", '"')
    if insert_count > 100:
        _query(sql_insert)
        insert_count = 0
    else:
        sql_insert += f"""insert into pools_pancake (id, pool_contract, token0_contract, token0_symbol, token0_decimals, token0_name,
         token1_contract, token1_symbol, token1_decimals, token1_name, is_active)
        VALUES('{pool_id}','{pool_contract}', '{token0_contract}', '{token0_symbol}', '{token0_decimals}', '{token0_name}',
               '{token1_contract}', '{token1_symbol}', '{token1_decimals}', '{token1_name}', true) ON CONFLICT (id) DO NOTHING;
               """
        insert_count += 1


def get_token_info(addr):
    address = Web3.toChecksumAddress(addr)
    token_factory = w3http.eth.contract(address=address, abi=ABIPoolPancake)
    token_name = token_factory.functions.name().call()
    token_symbol = token_factory.functions.symbol().call()
    token_decimals = token_factory.functions.decimals().call()
    return token_name, token_symbol, token_decimals


def get_pool_info(addr):
    address = Web3.toChecksumAddress(addr)
    pool_factory = w3http.eth.contract(address=address, abi=ABIPoolPancake)
    symbol = pool_factory.functions.symbol().call()
    token0_contract = pool_factory.functions.token0().call()
    token0_name, token0_symbol, token0_decimals = get_token_info(token0_contract)
    token1_contract = pool_factory.functions.token1().call()
    token1_name, token1_symbol, token1_decimals = get_token_info(token1_contract)
    return token0_contract, token0_name, token0_symbol, token0_decimals, token1_contract, token1_name, token1_symbol, token1_decimals


def run():
    pools_n = (_query("select id from pools_pancake order by id DESC limit 1;"))[0][0]
    pools_count = pancake_factory.functions.allPairsLength().call()
    print(pools_count)
    pool_id = pools_n + 1
    while pool_id < pools_count:
        print(pool_id, pools_count - pool_id)
        pool_contract = pancake_factory.functions.allPairs(pool_id).call()
        try:
            token0_contract, token0_name, token0_symbol, token0_decimals, token1_contract, token1_name, token1_symbol, token1_decimals = get_pool_info(
                pool_contract)
            add_pool(pool_id, pool_contract, token0_contract, token0_name, token0_symbol, token0_decimals,
                     token1_contract, token1_name, token1_symbol, token1_decimals)
        except Exception as err:
            print('error:', err, pool_id, pool_contract)
        pool_id += 1


run()
# if __name__ == '__name__':
#     asyncio.run(run())
