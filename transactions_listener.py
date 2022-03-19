import asyncio
import os
import redis
import traceback
from sqlalchemy import select

from web3 import Web3
from models.db.settings import Settings
from services.liquidation_service import LiquidationService
from services.users_service import UsersService
from toolkit import toolkit_
from pools import LendingPool
from db.engine import session, create_tables
from logger import log

HEALTH_FACTOR_THRESHOLD = toolkit_.w3.toWei(1, 'ether')
# HEALTH_FACTOR_THRESHOLD = 1251659644431660172

class TransactionsListener:

    def __init__(self) -> None:
        self._users_service = None
    
    @property
    def users_service(self):
        if not self._users_service:
            self._users_service = UsersService()
        return self._users_service
    
    # define function to handle events and print to the console
    def handle_event(self, event):
        # try:
        event_str = Web3.toJSON(event)
        # print(event_str)
        # event_type = event.get('event')

        # Add TEST_ prefix if not on mainnet
        # key = f'{user}' if 'mainnet' in consts.PROVIDER_URL else f'TEST_{user}'
        # Save the user data
        # fixed_args = {field: str(val) if isinstance(val, bool) else val for field,val in event.args.items()}
        # redis.hmset(key, fixed_args)

        # Check health factor
        user = event.args.get('user')
        exists, user_data = self.users_service.get_user_data(user)
        user_data.id = user
        self.users_service.save_user(user_data)
        health_factor = user_data.health_factor if user_data else HEALTH_FACTOR_THRESHOLD+1
        if health_factor < HEALTH_FACTOR_THRESHOLD:
            log.info(f"Health factor for user {user} is {health_factor}")
            # print(f"Health factor for user {user} is {health_factor}")
            liquidation_svc = LiquidationService()
            liquidation_svc.liquidate(user)
        # except Exception as e:
        #     print(f"Error: {e}")
        #     raise e
        # finally:
        #     session.close()


    # async def liquidate(user: str, debt_to_cover: str)

    # asynchronous defined function to loop
    # this loop sets up an event filter and is looking for new entires for the "PairCreated" event
    # this loop runs on a poll interval
    # async def log_loop(event_filter, poll_interval):
    #     while True:
    #         for PairCreated in event_filter.get_new_entries():
    #             handle_event(PairCreated)
    #         await asyncio.sleep(poll_interval)

    def get_events(self, block, len):
        try:
            if not toolkit_.is_connected():
                log.error("Disconnected from node")
                return

            toolkit_.trace_resource_usage()
            # start_block = 29756569 # Kovan
            # I started scanning backwards from block 1427961
            start_block = block # 14243784
            from_block = start_block-len
            to_block=start_block
            withdraw_events = LendingPool.events.Withdraw.getLogs(fromBlock=from_block, toBlock=to_block)
            borrow_events = LendingPool.events.Borrow.getLogs(fromBlock=from_block, toBlock=to_block)
            repay_events = LendingPool.events.Repay.getLogs(fromBlock=from_block, toBlock=to_block)
            # current_block = toolkit_.w3.eth.get_block_number()
            liquidate_events = LendingPool.events.LiquidationCall.getLogs(fromBlock=from_block, toBlock=to_block)
            deposit_events = LendingPool.events.Deposit.getLogs(fromBlock=from_block, toBlock=to_block)
            # flashloan_events = LendingPool.events.FlashLoan.getLogs(fromBlock=start_block-5, toBlock=start_block+5)
            # for e in borrow_events + withdraw_events + liquidate_events + repay_events + deposit_events:
            for e in borrow_events + withdraw_events + repay_events + deposit_events:# + repay_events + flashloan_events + liquidation_events:
                yield e
            log.info("Finished retrieving events")
        except Exception as e:
            log.error(f"Error retrieving events.\n Error: \
                {traceback.print_exc()}")
            return None

    def collect_user_data(self, events: list):
        try:
            asyncio.run(self.users_service.collect_user_data(events))
        except:
            # session.rollback()
            log.error(f'Error collecting user data \
                {traceback.print_exc()}')

def run():
    try:
        start_block = toolkit_.redis.get('CURR_BLOCK')  # in MB 
        if not start_block:
            start_block = session.query(Settings).get('LAST_BLOCK').value
            log.info('Loaded start block from DB')

        curr_block = int(start_block)
        log.info(f'Start block: {start_block}')
        events_len = int(os.environ.get('EVENTS_LENGTH'))
        listener = TransactionsListener()
        for i in range (1, int(os.environ.get('MAX_EVENT_SCAN_ITERATIONS'))):
            log.info(f'Retrieving events from block {curr_block}')
            events = listener.get_events(curr_block, events_len)
            log.info("Collecting user data")
            # start_time = time.process_time()
            listener.collect_user_data(events)
            curr_block -= events_len
            toolkit_.redis.set('CURR_BLOCK', curr_block)
            session.query(Settings).filter_by(name='LAST_BLOCK').update({"value": curr_block})
            session.commit()

            # end_time = time.process_time()
            # print(f'Data collection took {end_time - start_time}')
        log.info(f'Done.')
    except Exception as e:
        log.error(f'Error in Liquidator.\n Error: \
                {traceback.print_exc()}')
    finally:
        session.close()

# def add_user_reserves(users):
#     svc = UsersService()
#     # borrowers = ['0xdde9C12718217F792228AC1ce4c4a04a92b15735','0x008c8395eAbA2553CDE019aF1Be19A89630E031F']
#     for user in users:
#         collaterals, debts = svc.get_collaterals_and_debts(user)
#         if not collaterals and not debts:
#             continue
#         try:
#             #TODO: fix this, saves empty records.
#             svc.save_user_reserve_data([c['userReserveData'] for c in collaterals + debts])
#         except:
#             pass

def main():
    # add_user_reserves(['0xa25A9b7c73158B3B34215925796Ce6Aa8100C13a'])
    val = 27519318177421073050
    # conv = val.astype(int).item()
    create_tables()

    # from models.db.settings import Settings
    # session.add(Settings('LAST_BLOCK', 14243384))
    # session.commit()
    run()


    # value = toolkit_.w3.fromWei(200917325452379653357, 'ether')
    # debtToCover = 3553656655
    # debtPriceUsd = 382283014377909
    # debt_eth = toolkit_.w3.fromWei(debtToCover, 'ether')
    # debtPriceUsd_eth = toolkit_.w3.fromWei(debtPriceUsd, 'ether')
    # collateralPriceLink = toolkit_.w3.fromWei(5343808813475518, 'ether')
    # bonus = toolkit_.w3.fromWei(10650, 'ether')
    # to_liquidate = toolkit_.w3.fromWei(1470593284631612599, 'ether')
    # gas = toolkit_.w3.fromWei(48561, 'ether')
    # maxGas = toolkit_.w3.fromWei(18348798341403870831, 'ether')

    # if not is_connected():
    #     return

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