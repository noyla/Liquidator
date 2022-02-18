import json
import asyncio
import redis
from assets_service import AssetsService
import consts

from web3 import Web3
from toolkit import LendingPool, Toolkit

# add your blockchain connection information
# provider_url = "https://kovan.infura.io/v3/cf34bf113ea14801a4d33a9db6822e5b"
# provider_url = "https://tegzjp8pmscy.usemoralis.com:2053/server"
web3 = Web3(Web3.HTTPProvider(consts.PROVIDER_URL))

# aave_kovan_contract_address = '0x2646FcF7F0AbB1ff279ED9845AdE04019C907EBE'
aave_kovan_contract_address = '0xE0fBa4Fc209b4948668006B2bE61711b7f465bAe'
# Borrow / Deposit / Repay / LiquidationCall
aave_factory_abi = json.loads('[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"reserve","type":"address"},{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":true,"internalType":"address","name":"repayer","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Repay","type":"event"},'
                              '{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"reserve","type":"address"},{"indexed":false,"internalType":"address","name":"user","type":"address"},{"indexed":true,"internalType":"address","name":"onBehalfOf","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"borrowRateMode","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"borrowRate","type":"uint256"},{"indexed":true,"internalType":"uint16","name":"referral","type":"uint16"}],"name":"Borrow","type":"event"},'
                              '{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"reserve","type":"address"},{"indexed":false,"internalType":"address","name":"user","type":"address"},{"indexed":true,"internalType":"address","name":"onBehalfOf","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":true,"internalType":"uint16","name":"referral","type":"uint16"}],"name":"Deposit","type":"event"},'
                              '{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"collateralAsset","type":"address"},{"indexed":true,"internalType":"address","name":"debtAsset","type":"address"},{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"debtToCover","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"liquidatedCollateralAmount","type":"uint256"},{"indexed":false,"internalType":"address","name":"liquidator","type":"address"},{"indexed":false,"internalType":"bool","name":"receiveAToken","type":"bool"}],"name":"LiquidationCall","type":"event"},'
                              '{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"target","type":"address"},{"indexed":true,"internalType":"address","name":"initiator","type":"address"},{"indexed":true,"internalType":"address","name":"asset","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"premium","type":"uint256"},{"indexed":false,"internalType":"uint16","name":"referralCode","type":"uint16"}],"name":"FlashLoan","type":"event"},'
                              '{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"getUserAccountData","outputs":[{"internalType":"uint256","name":"totalCollateralETH","type":"uint256"},{"internalType":"uint256","name":"totalDebtETH","type":"uint256"},{"internalType":"uint256","name":"availableBorrowsETH","type":"uint256"},{"internalType":"uint256","name":"currentLiquidationThreshold","type":"uint256"},{"internalType":"uint256","name":"ltv","type":"uint256"},{"internalType":"uint256","name":"healthFactor","type":"uint256"}],"stateMutability":"view","type":"function"}]')
contract = web3.eth.contract(address=aave_kovan_contract_address, abi=aave_factory_abi)
topics = [web3.sha3(text='Deposit(address,address,address,uint256,uint16)').hex()]
redis = redis.Redis(host='localhost', port=6379)

HEALTH_FACTOR_THRESHOLD = 1000000000000000000

def is_connected():
    is_connected = web3.isConnected()
    print(is_connected)
    return is_connected

# define function to handle events and print to the console
def handle_event(event):
    event_str = Web3.toJSON(event)
    print(event_str)
    user = event.args.get('user')
    on_behalf = event.args.get('onBehalfOf')
    reserve = event.args.get('reserve')
    amount = event.args.get('amount')
    referral = event.args.get('referral')
    event_type = event.get('event')
    tx_hash = event.get('transactionHash')
    redis.set(user, event_str)




# asynchronous defined function to loop
# this loop sets up an event filter and is looking for new entires for the "PairCreated" event
# this loop runs on a poll interval
# async def log_loop(event_filter, poll_interval):
#     while True:
#         for PairCreated in event_filter.get_new_entries():
#             handle_event(PairCreated)
#         await asyncio.sleep(poll_interval)

def get_events():
    assets_svc = AssetsService()
    aave = assets_svc.get_asset("AAVE")
    lending_pool = Toolkit.getContractInstance(LendingPool.address, "LENDING_POOL.json")

    start_block = 29756569
    flashloan_event_filter = lending_pool.events.FlashLoan.createFilter(fromBlock=start_block-5, toBlock=start_block-1)
    deposit_event_filter = lending_pool.events.Deposit.createFilter(fromBlock=start_block-5)
    borrow_event_filter = lending_pool.events.Borrow.createFilter(fromBlock=29756569)
    repay_event_filter = lending_pool.events.Repay.createFilter(fromBlock=29756569)
    for FlashLoan in flashloan_event_filter.get_all_entries():
        handle_event(FlashLoan)
    for Deposit in deposit_event_filter.get_all_entries():
        handle_event(Deposit)
    for Borrow in borrow_event_filter.get_all_entries():
        handle_event(Borrow)
    for Repay in repay_event_filter.get_all_entries():
        handle_event(Repay)


def check_user_health(address: str):
    user_data = contract.functions.getUserAccountData(address).call()
    if not user_data:
        return
    user_data = {'totalCollateralETH': user_data[0], 'totalDebtETH': user_data[1], 'availableBorrowsETH': user_data[2],
                 'currentLiquidationThreshold': user_data[3], 'ltv': user_data[4], 'healthFactor': user_data[5]}
    print(user_data)

# def liquidate(address: str):
#     collateral = DAI_KOVAN_ADDRESS
#     reserve = BUSD_KOVAN_ADDRESS
#     purchase_amount = -1
#     receive_token = False
#     dai.address.add
#     contract.functions.liquidationCall(address).call()

# when main is called
# create a filter for the latest block and look for the "PairCreated" event for the uniswap factory contract
# run an async loop
# try to run the log_loop function above every 2 seconds
def main():
    # event_filter = web3.eth.filter({'address': aave_kovan_contract_address, 'fromBlock': 29756569})
    # logs = web3.eth.getFilterLogs(event_filter.filter_id)
    # print(logs)
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