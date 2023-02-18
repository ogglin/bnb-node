from web3 import Web3

from .abis import PancakeV2Factory, PancakeRouterV2, PancakeMainStakingContractV2, ABIPoolPancake, ABIPancakeToken

bsc = 'http://91.215.61.140:28545'
bsc_wss = 'ws://91.215.61.140:28888'
w3http = Web3(Web3.HTTPProvider(bsc))
# w3wss = Web3(Web3.WebsocketProvider(bsc_wss))

pancake_factory_address = Web3.toChecksumAddress('0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73')
pancake_factory = w3http.eth.contract(address=pancake_factory_address, abi=PancakeV2Factory)
# wss_pancake_factory = w3wss.eth.contract(address=pancake_factory_address, abi=PancakeV2Factory)


# Binance-Peg Ethereum Token - 0x2170Ed0880ac9A755fd29B2688956BD959F933F8
# Binance-Peg BUSD Token 0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56
# Binance-Peg BSC-USD 0x55d398326f99059fF775485246999027B3197955
# Wrapped BNB 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c
# Binance-Peg USD Coin (USDC) 0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d

stable_coins = [
    '0x2170Ed0880ac9A755fd29B2688956BD959F933F8',
    '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56',
    '0x55d398326f99059fF775485246999027B3197955',
    '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
    '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',
]