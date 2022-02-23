import copy
import json
import asyncio
import redis
from assets_service import AssetsService
import consts

from web3 import Web3
from liquidation_service import LiquidationService
from toolkit import toolkit_
from pools import LendingPool

redis = redis.Redis(host='localhost', port=6379)

HEALTH_FACTOR_THRESHOLD = 1000000000000000000
HEALTH_FACTOR_THRESHOLD = 1151659644431660172

def get_user_data(address: str):
    user_data = LendingPool.functions.getUserAccountData(address).call()
    if not user_data:
        return None
    user_data = {'totalCollateralETH': user_data[0], 'totalDebtETH': user_data[1], 'availableBorrowsETH': user_data[2],
                 'currentLiquidationThreshold': user_data[3], 'ltv': user_data[4], 'healthFactor': user_data[5]}
    print(user_data)
    return user_data

def is_connected():
    is_connected = toolkit_.w3.isConnected()
    print(is_connected)
    return is_connected


# define function to handle events and print to the console
def handle_event(event):
    event_str = Web3.toJSON(event)
    print(event_str)
    event_type = event.get('event')
    user = event.args.get('user')
    # Add TEST_ prefix if not on mainnet
    key = f'USER_{user}' if 'mainnet' in consts.PROVIDER_URL else f'TEST_USER_{user}'

    # Save the user data
    fixed_args = {field: str(val) if isinstance(val, bool) else val for field,val in event.args.items()}
    redis.hmset(key, fixed_args)

    # Check health factor
    user_data = get_user_data(user)
    health_factor = user_data['healthFactor'] if user_data else HEALTH_FACTOR_THRESHOLD+1
    if health_factor < HEALTH_FACTOR_THRESHOLD:
        print(f"Health factor for user {user} is {health_factor}")
        liquidation_svc = LiquidationService()
        liquidation_svc.liquidate(user)

# async def liquidate(user: str, debt_to_cover: str)

# asynchronous defined function to loop
# this loop sets up an event filter and is looking for new entires for the "PairCreated" event
# this loop runs on a poll interval
# async def log_loop(event_filter, poll_interval):
#     while True:
#         for PairCreated in event_filter.get_new_entries():
#             handle_event(PairCreated)
#         await asyncio.sleep(poll_interval)

def get_events():
    # start_block = 29756569 # Kovan
    start_block = 14230925 # Mainnet
    # withdraw_events = LendingPool.events.Withdraw.getLogs(fromBlock=start_block-500, toBlock=start_block)
    # borrow_events = LendingPool.events.Borrow.getLogs(fromBlock=start_block-500, toBlock=start_block)
    repay_events = LendingPool.events.Repay.getLogs(fromBlock=start_block-1, toBlock=start_block+1)
    liquidate_events = LendingPool.events.LiquidationCall.getLogs(fromBlock=start_block-1, toBlock=start_block+1)
    # deposit_events = LendingPool.events.Deposit.getLogs(fromBlock=start_block-5, toBlock=start_block+10)
    flashloan_events = LendingPool.events.FlashLoan.getLogs(fromBlock=start_block-1, toBlock=start_block+1)
    # for e in borrow_events + withdraw_events + liquidate_events + repay_events + deposit_events:
    for e in liquidate_events + repay_events + flashloan_events:
        handle_event(e)
    # for e in withdraw_events:
    #     handle_event(e)
    # for e in repay_events:
    #     handle_event(e)
    # for e in liquidate_events:
    #     handle_event(e)
    # for e in flashloan_events:
        # handle_event(e)
    # for Deposit in deposit_events:
    #     handle_event(Deposit)
    print("Done")


def main():
    # gas = toolkit_.w3.fromWei(48561, 'ether')
    debtToCover = 2895911583
    debtPriceUsd = 382283014377909
    debt_eth = toolkit_.w3.fromWei(debtToCover, 'ether')
    debtPriceUsd_eth = toolkit_.w3.fromWei(debtPriceUsd, 'ether')
    collateralPriceLink = toolkit_.w3.fromWei(5343808813475518, 'ether')
    bonus = toolkit_.w3.fromWei(10650, 'ether')
    to_liquidate = toolkit_.w3.fromWei(39713805163032, 'ether')
    gas = toolkit_.w3.fromWei(48561, 'ether')
    maxGas = toolkit_.w3.fromWei(18348798341403870831, 'ether')

    if not is_connected():
        return
    get_events()

    # check_user_health('0x9998b4021d410c1E8A7C512EF68c9d613B5B1667')
    # check_user_health('0x6208F0064bCdE3eA0A57c3a905cC3201fFb28Ff0')

    # event_filter = contract.events.PairCreated.createFilter(fromBlock='latest')
    #block_filter = web3.eth.filter('latest')
    # tx_filter = web3.eth.filter('pending')
    # loop = asyncio.get_event_loop()
    # try:
    #     loop.run_until_complete(
    #         asyncio.gather(
    #             log_loop(event_filter, 2)))
    #     log_loop(block_filter, 2),
    #     log_loop(tx_filter, 2)))
    # finally:
    #     close loop to free up system resources
        # loop.close()


if __name__ == "__main__":
    main()