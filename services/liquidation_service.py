import math

import consts
from typing import Tuple
from services.assets_service import AssetsService
from services.contracts_service import ContractsService
from services.users_service import UsersService
from toolkit import toolkit_
from pools import LendingPool
from models.db.user_reserve_data import UserReserveData
from logger import log

class LiquidationService:
    def __init__(self):
        self._assets_service = None
        self._users_service = None
    
    @property
    def assets_service(self):
        if not self._assets_service:
            self._assets_service = AssetsService()
        return self._assets_service
    
    @property
    def users_service(self):
        if not self._users_service:
            self._users_service = UsersService()
        return self._users_service

    def check_liquidation_profitability(self, borrower: str) -> \
                                        Tuple[UserReserveData, str, float, str, int]:
        """
        Gets liquidation info of user collaterals.
        Calculating which reserve has the best profit

        Args:
            borrower (str): Borrower user address

        Returns:
            Tuple[UserData, Web3.eth.Eth.contract]: Returns user data and the reserve contract
        """
        collaterals, debts = self.users_service.get_collaterals_and_debts(borrower)
        self.users_service.save_user_reserve_data([c['userReserveData'] for c in collaterals + debts])
        if not (collaterals and debts):
            log(f"Found {len(collateral)} collaterals and {len(debts)} borrowd assets.\n"
                  f"cannot liquidate user {borrower}")
            return
        
        # Find the most profitable collateral
        # Calculate profitability of liquidation. Check currentATokenBalance
        curr_debt = (0,None)
        for d in debts:
            debtToCover = self.calculate_debt_to_cover(d.get('userReserveData'))
            d['debtToCover'] = debtToCover
            if debtToCover > curr_debt[0]:
                curr_debt = (debtToCover, d)
        chosen_debt = curr_debt[1]
        debt_contract = self.assets_service.get_asset(
            chosen_debt['userReserveData'].reserve)
        debtToCover = chosen_debt['debtToCover']
        chosen_debt['debtPrice'] = self.assets_service.get_asset_price(
            chosen_debt['userReserveData'].reserve)
        # chosen_debt['gasEstimation'] = chosen_debt['debtPrice'] * gas_estimation
            # (approval_gasEstimation + liquidation_gasEstimation)
        
        for collateral in collaterals:            
            reserve = collateral.get('userReserveData').reserve           
            collateral_price = self.assets_service.get_asset_price(reserve)
            reserve_configurations = self.assets_service.get_reserve_configuraion_data(reserve)
            collateral['bonus'] = reserve_configurations.liquidation_bonus
            decimals = reserve_configurations.decimals

            collateral['liquidated_collateral_amount'] = (chosen_debt['debtPrice'] * debtToCover * collateral['bonus']) / \
                collateral_price * decimals
            
            log.info(f"Max liquidated collateral for reserve {reserve}: {collateral['liquidated_collateral_amount']}")
        
        # Choose the maximum collateral to receive
        chosen_collateral = max(collaterals, key=lambda c: c['liquidated_collateral_amount'])
        collateral_contract = self.assets_service.get_asset(chosen_collateral['userReserveData'].reserve)

        # Estimate gas
        approval_gas_estimation = debt_contract.functions.approve(
            LendingPool.address, debtToCover).estimateGas()
            # toolkit_.account.address, debtToCover).estimateGas()
        
        # TODO: Make liquidation estimateGas() work
        # liquidation_gas_estimation = LendingPool.functions.liquidationCall(collateral_contract.address, 
        #     debt_contract.address, # Debt asset
        #     borrower, # User to liquidate
        #     debtToCover, # Amount of debt to cover
        #     # chosen_collateral['liquidated_collateral_amount'], # Amount of collateral to liquidate
        #     # toolkit_.account.address, # Liquidator address
        #     True).estimateGas()
        liquidation_gas_estimation = approval_gas_estimation
        chosen_debt['gasEstimation'] = {'approval': approval_gas_estimation,
                                        'iquidation': liquidation_gas_estimation}

        max_income = chosen_collateral['userReserveData'].current_aToken_balance * \
                     toolkit_.w3.fromWei(collateral_price, 'ether') * \
                     chosen_collateral['bonus']
        max_fees = chosen_debt['debtPrice'] * \
                   (approval_gas_estimation + liquidation_gas_estimation)
        profit = max_income - max_fees
        if profit <= 0:
            raise Exception(f"Liquidation non profitable for {borrower}.")
        return collateral_contract, chosen_collateral['liquidated_collateral_amount'], \
               debt_contract, debtToCover, chosen_debt['gasEstimation']
                        

    def liquidate(self, borrower: str) -> str:
        collateral_contract, liquidated_collateral_amount, debt_contract, \
        debtToCover, gas = self.check_liquidation_profitability(borrower)
        
        # Balance check
        balance = self.assets_service.get_balance(debt_contract)
        if balance < debtToCover:
            log.info(f"Not enough funds to liquidate debt.\n \
                    Asset address: {debt_contract.address}")
            return

        allowance = self.assets_service.get_allowance()
        if allowance <= 0:
            approval_hash = self.assets_service.approve(debt_contract, debtToCover, 
                                                        gas['approval'])
            # approval_hash = ContractsService.exec_contract(self.account, nonce, 
            #                 debt_asset_contract.functions.approve(LendingPool.address, debtToCover))
        
        
        # liquidatedCollateralAmount = 1 #.toWei(d, 'ether')
        liquidation_func = LendingPool.functions.liquidationCall(
            collateral_contract.address, # Collateral asset
            debt_contract.address, # Debt asset
            borrower, # User to liquidate
            debtToCover, # Amount of debt to cover
            # liquidated_collateral_amount, # Amount of collateral to liquidate
            # toolkit_.account.address, # Liquidator address
            True # Receive aToken
        )
        nonce = toolkit_.w3.eth.getTransactionCount(toolkit_.account.address)
        liquidation_hash = ContractsService.exec_contract(toolkit_.account, nonce, 
                                                          liquidation_func, 
                                                          gas['liquidation'])

    def calculate_debt_to_cover(self, user_reserve_data: UserReserveData):
        debtToCover = math.floor((user_reserve_data.current_stable_debt + user_reserve_data.current_variable_debt) * \
                        consts.LIQUIDATION_CLOSE_FACTOR)
        # debtToCover2 = math.floor(user_data.currentATokenBalance * consts.LIQUIDATION_CLOSE_FACTOR)
        # TODO: check wei conversion, should use asset and not ether.
        return debtToCover
