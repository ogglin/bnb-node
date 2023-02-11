import json
from pathlib import Path

with open(str(Path(__file__).resolve(strict=True).parent) + "/Factory v2.json", "r") as infile:
    val = infile.read()
    PancakeV2Factory = json.loads(val)

with open(str(Path(__file__).resolve(strict=True).parent) + "/Main Staking Contract V2.json", "r") as infile:
    val = infile.read()
    PancakeMainStakingContractV2 = json.loads(val)

with open(str(Path(__file__).resolve(strict=True).parent) + "/Router v2.json", "r") as infile:
    val = infile.read()
    PancakeRouterV2 = json.loads(val)

with open(str(Path(__file__).resolve(strict=True).parent) + "/PoolPancake.json", "r") as infile:
    val = infile.read()
    ABIPoolPancake = json.loads(val)

with open(str(Path(__file__).resolve(strict=True).parent) + "/ABIPancakeToken.json", "r") as infile:
    val = infile.read()
    ABIPancakeToken = json.loads(val)
