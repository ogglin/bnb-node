import asyncio

from web3 import Web3
from web3.middleware import geth_poa_middleware

from pancake import w3http
from pancake.services.get_all_pairs import run

bsc = 'http://192.168.68.105:8545'
web3 = Web3(Web3.HTTPProvider(bsc))
# web3.middleware_onion.inject(geth_poa_middleware, layer=0)

print(web3.isConnected())
# print(web3.eth.get_block(25027145))
sync = web3.eth.syncing
if sync:
    for k, v in sync.__dict__.items():
        print(k, v)
# print(w3http.eth.syncing.__dict__['currentBlock'])
# print(w3http.eth.syncing.__dict__['highestBlock'])


async def main():
    await run()
    print(web3.isConnected())
    print(web3.eth.syncing)


if __name__ == '__name__':
    asyncio.run(main())
