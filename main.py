import asyncio

from pancake.services.get_pool_info import run_pools


async def main():
    await run_pools()


if __name__ == '__main__':
    asyncio.run(main())
