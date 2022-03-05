import asyncio
import functools
import json
from operator import and_
import traceback

import redis
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


class UsersService:
    def __init__(self) -> None:
        self.protocolDataProvider = ContractsService.getContractInstance(consts.PROTOCOL_DATA_PROVIDER, 
        "PROTOCOL_DATA_PROVIDER.json")
        self._assets_service = None
        self._users_store = None
        self.redis = redis.Redis()
    
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
        exists = self.redis.exists(address)
        if exists:
            return True, self.redis.hgetall(address)

        user_data = LendingPool.functions.getUserAccountData(address).call()
        if not user_data:
            return None
        user_data = {'totalCollateralETH': user_data[0], 'totalDebtETH': user_data[1], 'availableBorrowsETH': user_data[2],
                    'currentLiquidationThreshold': user_data[3], 'ltv': user_data[4], 'healthFactor': user_data[5]}
        print(user_data)
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
            user_data = self.get_user_reserve_data(name, user)
            if user_data:
                if user_data.current_aToken_balance != 0 and user_data.usage_as_collateral_enabled:
                    user_data.reserve = name
                    collaterals.append({'userReserveData': user_data})#, 
                                #'reserve': name})
                    print(f'User Reserve Data for reserve {name}: {json.dumps(user_data.to_dict())}')
                elif user_data.current_stable_debt or user_data.current_variable_debt:
                    user_data.reserve = name
                    debts.append({'userReserveData': user_data})#,
                                # 'reserve': name})
                    print(f'User Reserve Data for reserve {name}: {json.dumps(user_data.to_dict())}')
        
        return collaterals, debts
    
    def save_user_reserve_data(self, user_reserve_data: list[UserReserveData]):
        existing_reserves = session.query(UserReserveData).with_entities(
            func.concat(UserReserveData.user, '_', UserReserveData.reserve)).filter(
            UserReserveData.id.in_([d.id for d in user_reserve_data])).all()
        for data in user_reserve_data:
            data.id = data.user + '_' + data.reserve
            insp = inspect(data)
            if data.id in existing_reserves or (insp.pending or 
            insp.persistent):
                continue
            session.merge(data)
        session.commit()
        with open(consts.USER_RESERVES_LOGS, 'a') as f:
                f.write(f'Saved reserves for user:\n {[d.id for d in user_reserve_data]}')
        
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
            with open(consts.USER_LOGS, 'a') as f:
                f.write(f'Saved user {user_data.id}\n')


    async def collect_user_data(self, events):
        # with session.no_autoflush:
        # with session.bind.begin() as conn:
        try:
            count = 0
            users = {}
            users_reserves = []
            tasks = []
            for event in events:
                # tasks.append(asyncio.create_task(self.collect(event)))
                tasks.append(functools.partial(self.collect, event))
                
                # user, user_reserve =  await task
            
            # Schedule three calls *concurrently*:
            res = await asyncio.gather(*[func() for func in tasks])
            for data in res:
                user = data[0]
                user_reserves = data[1]
                if not user and not user_reserves:
                    continue
                users[user.id] = user
                users_reserves.extend(user_reserves)
                count += 1
                if count >= 6:
                    # session.commit()
                    self.users_store.create_users_with_reserves(users, 
                                    users_reserves)
                    users.clear()
                    users_reserves.clear()
                    count = 0
            # Commit any leftover users.
            if count % 10 != 0:
                self.users_store.create_users_with_reserves(users, 
                                    users_reserves)
        except:
            print('Error: %s', traceback.print_exc())

    
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
        exists, user_data = self.get_user_data(user)
        if exists:
            return {}, []
        user_data.id = user
        collaterals, debts = self.get_collaterals_and_debts(user)
        # self.save_user(user_data)
        self.redis.hset(user_data.id, mapping=user_data.to_dict())

        if collaterals or debts:
            return user_data, [c['userReserveData'] for c in collaterals + debts]
            # self.save_user_reserve_data([c['userReserveData'] for c in collaterals + debts])
        return user_data, []
    
    def migrate_to_redis(self):
        users = session.query(User).all()
        for u in users:
            self.redis.hset(u.id, mapping=u.to_dict())


