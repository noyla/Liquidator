import asyncio
import time
import traceback
import consts

from typing import Tuple
from db.engine import session
from models.db.user import User
from models.db.user_reserve_data import UserReserveData
from pools import LendingPool
from services.assets_service import AssetsService
from services.contracts_service import ContractsService
from stores.users_store import UsersStore
from toolkit import toolkit_
from sqlalchemy import inspect, func
from logger import log

start_time = None
end_time = None

class UsersService:
    def __init__(self) -> None:
        self.protocolDataProvider = ContractsService.getContractInstance(consts.PROTOCOL_DATA_PROVIDER, 
        "PROTOCOL_DATA_PROVIDER.json")
        self._assets_service = None
        self._users_store = None
        # self.redis = redis.Redis(charset="utf-8", decode_responses=True)
    
    @property
    def assets_service(self):
        if not self._assets_service:
            self._assets_service = AssetsService()
        return self._assets_service
    
    @property
    def users_store(self):
        if not self._users_store:
            self._users_store = UsersStore()
        return self._users_store

    def get_user_data(self, address: str) -> Tuple[bool, User]:
        # exists = self.redis.exists(address)
        exists = toolkit_.redis.exists(address)
        if exists:
            # Temporary redis bug partial user data, if exception occurs,
            # Move on and retrieve data from the API.
            try:
                # user = User.from_dict(self.redis.hgetall(address))
                user = User.from_dict(toolkit_.redis.hgetall(address))
                return True, user
            except:
                log.error(f'Error getting user data \n Error: \
                    {traceback.print_exc()}')
        else:
            user = session.query(User).filter_by(id=address).first()
            if user:
                log.debug(f'Loaded user {user.id}')
                toolkit_.redis.hset(user.id, mapping=user.to_dict())
                log.debug(f'Saved user {user.id} to redis')
                return True, user

            
        user_data = LendingPool.functions.getUserAccountData(address).call()
        if not user_data:
            return None
        user_data = {'id': address, 'total_collateral_eth': user_data[0], 'total_debt_eth': user_data[1], 'available_borrows_eth': user_data[2],
                    'current_liquidation_threshold': user_data[3], 'ltv': user_data[4], 'health_factor': user_data[5]}
        log.debug(f'User data: {user_data}')
        return False, User.from_dict(user_data)
    
    def get_balance(self, asset_contract: str) -> int:
        return asset_contract.functions.balanceOf(toolkit_.account.address).call()
    
    def get_user_reserve_data(self, asset: str, user: str) -> UserReserveData:
        asset_address = self.assets_service.reserves.get(asset, None)
        user_data = self.protocolDataProvider.functions.getUserReserveData(asset_address, user).call()
        if not user_data:
            return None
        user_data.append(asset)
        user_data.append(user)
        return UserReserveData.from_raw_list(user_data)
    
    def get_collaterals_and_debts(self, user: str) -> Tuple[dict, dict]:
        collaterals = []
        debts = []
        for name, address in self.assets_service.reserves.items():
            # self.assets_service.get_reserve_configuraion_data(name)
            user_data = self.get_user_reserve_data(name, user)
            if user_data:
                if user_data.current_aToken_balance != 0 and user_data.usage_as_collateral_enabled:
                    user_data.reserve = name
                    user_data.id = user_data.user + '_' + user_data.reserve
                    collaterals.append({'userReserveData': user_data})#, 
                                #'reserve': name})
                    # log.info(f'User Reserve Data for reserve {name}: \
                    #         {json.dumps(user_data.to_dict())}')
                elif user_data.current_stable_debt or user_data.current_variable_debt:
                    user_data.reserve = name
                    user_data.id = user_data.user + '_' + user_data.reserve
                    debts.append({'userReserveData': user_data})#,
                                # 'reserve': name})
                    # log.info(f'User Reserve Data for reserve {name}: \
                    #     {json.dumps(user_data.to_dict())}')
        
        return collaterals, debts
    
    def save_user_reserve_data(self, user_reserve_data: list[UserReserveData]):
        existing_reserves = session.query(UserReserveData).with_entities(
            func.concat(UserReserveData.user, '_', UserReserveData.reserve)).filter(
            UserReserveData.id.in_([d.id for d in user_reserve_data])).all()
        for data in user_reserve_data:
            data.id = data.user + '_' + data.reserve
            insp = inspect(data)
            # if data.id in existing_reserves or (insp.pending or 
            # insp.persistent):
            #     continue
            session.merge(data)
        session.commit()
        log.info(f'Saved reserves for user:\n \
                {[d.id for d in user_reserve_data]}')
        # with open(consts.USER_RESERVES_LOGS, 'a') as f:
        #         f.write(f'Saved reserves for user:\n {[d.id for d in user_reserve_data]}')
        
        # if not exists and not (insp.pending or insp.transient or insp.persistent):
        # session.add_all(user_reserve_data)
        # session.commit()
        # session.saveorupdate(user_reserve_data)

    def save_user(self, user_data: User):
        # session.add(user_data)
        # exists = session.query(exists().where(User.id == user_data.id)).scalar()
        q = session.query(User).filter(User.id == user_data.id)
        exists = session.query(q.exists()).scalar()
        insp = inspect(user_data)
        if not exists and not (insp.pending or insp.persistent):
            session.add(user_data)
            session.commit()
            log.info(f'Saved user {user_data.id}\n')
            # with open(consts.USER_LOGS, 'a') as f:
            #     f.write(f'Saved user {user_data.id}\n')


    async def collect_user_data(self, events):
        # with session.no_autoflush:
        # with session.bind.begin() as conn:
        try:
            count = 0
            tasks = []
            global start_time
            start_time = time.process_time()
            for event in events:
                tasks.append(asyncio.create_task(self.collect(event)))
                
                # tasks.append(functools.partial(self.collect, event))
                count += 1
                if count >= consts.TASK_BATCH_SIZE:
                    log.info('About to run collection')
                    toolkit_.trace_resource_usage()
                    res = await asyncio.gather(*[func for func in tasks])
                    if res:
                        await self.save_user_data_tuple(res)
                        log.info(f'Saved {len(res)} users reserve data')
                        toolkit_.trace_resource_usage()
                        tasks.clear()
                        count = 0
                
                # user, user_reserve =  await task
            
            # Schedule three calls *concurrently*:
            if count % 10 != 0:
                res = await asyncio.gather(*[func for func in tasks])
                if res:
                    await self.save_user_data_tuple(res)
                    log.info(f'Saved {len(res)} users reserve data')
            log.info('Finished processing all events')
            toolkit_.trace_resource_usage()
            # res = await asyncio.gather(*[func() for func in tasks])
        except:
            log.error('Error: {}'.format(traceback.print_exc()))

    async def save_user_data_tuple(self, res: list[User, UserReserveData]):
        try:
            users = {}
            users_reserves = []
            count = 0
            for data in res:
                user = data[0]
                user_reserves = data[1]
                if not user and not user_reserves:
                    continue
                users[user.id] = user
                if user_reserves:
                    users_reserves.extend(user_reserves)
                count += 1
                if count >= 20:
                    self.users_store.create_users_with_reserves(users, 
                                    users_reserves)
                    self.store_to_redis(users)
                    users.clear()
                    users_reserves.clear()
                    count = 0
            # Commit any leftover users.
            if count % 20 != 0:
                log.info('Storing leftovers from last batch')
                if users or users_reserves:
                    self.users_store.create_users_with_reserves(users, 
                                                                users_reserves)
                    self.store_to_redis(users)
            global end_time
            end_time = time.process_time()
            log.info(f'Data collection took {end_time - start_time}')
        except:
            log.error('Error: {}'.format(traceback.print_exc()))

    
    # async def collect_user_data(self, events):
    #     # with session.no_autoflush:
    #     try:
    #         # with session.bind.begin() as conn:
    #         count = 0
    #         for event in events:
    #             count += 1
    #             try:
    #                 task = asyncio.create_task(self.collect(event))
    #             except:
    #                 print('Error: %s', traceback.print_exc())    
    #                 continue
    #             user, user_reserves = await task
    #             # if count >= 6:
    #             #     session.commit()
    #             #     count = 0
    #         # Commit any leftover users.
    #         # if count % 10 != 0:
    #         #     session.commit()
    #     except:
    #         # session.rollback()
    #         print('Error: %s', traceback.print_exc())
    
    async def collect(self, event):
        user = event.args.get('user')
        svc = UsersService()
        exists, user_data = svc.get_user_data(user)
        if exists or not user_data:
            return {}, []
        user_data.id = user
        collaterals, debts = svc.get_collaterals_and_debts(user)

        if collaterals or debts:
            return user_data, [c['userReserveData'] for c in collaterals + debts]
            # self.save_user_reserve_data([c['userReserveData'] for c in collaterals + debts])
        return user_data, []
    
    def migrate_to_redis(self):
        users = session.query(User).all()
        for u in users:
            toolkit_.redis.hset(u.id, mapping=u.to_dict())
            # self.redis.hset(u.id, mapping=u.to_dict())
    
    def store_to_redis(self, users: dict[User]):
        # pipe = self.redis.pipeline()
        pipe = toolkit_.redis.pipeline()
        for id, u in users.items():
            pipe.hset(id, mapping=u.to_dict())
        pipe.execute()

