import math
import os
import consts
from asyncio.constants import DEBUG_STACK_DEPTH
from typing import Tuple
from assets_service import AssetsService
from contracts_service import ContractsService
from toolkit import toolkit_
from pools import LendingPool
from models.user_data import UserReserveData

class LiquidationService:
    def __init__(self):
        # self.account = toolkit.w3.eth.account.privateKeyToAccount(
        #     os.environ.get("ACCOUNT1_PRIVATE_KEY"))
        self.assets_service = AssetsService()

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
        # TODO: iterate the assets and call getUserReserveData, check what collateral we have 
        collaterals, debts = self.assets_service.get_collaterals_and_debts(borrower)
        if not (collaterals and debts):
            print(f"Found {len(collateral)} collaterals and {len(debts)} borrowd assets.\n"
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
        # chosen_debt = filter(lambda d: \
        #     max(self.calculate_debt_to_cover(d.get('userReserveData')), debts))
        # chosen_debt = next(iter(chosen_debt))
        debt_contract = self.assets_service.get_asset(chosen_debt['reserve'])
        debtToCover = chosen_debt['debtToCover']
        gas_estimation = debt_contract.functions.approve(
            LendingPool.address, debtToCover).estimateGas()
        # liquidation_gasEstimation = LendingPool.functions.liquidationCall().estimateGas() #TODO: complete args for liquidationcall
        chosen_debt['debtPrice'] = self.assets_service.get_asset_price(chosen_debt['reserve'])
        chosen_debt['gasEstimation'] = chosen_debt['debtPrice'] * gas_estimation
            # (approval_gasEstimation + liquidation_gasEstimation)
        
        for collateral in collaterals:
            # user_reserve_data = collateral.get('userReserveData')
            reserve = collateral.get('reserve')
            # asset_contract = self.assets_service.get_asset(reserve)
            collateral_price = self.assets_service.get_asset_price(reserve)
            # atoken_balance = user_reserve_data.currentATokenBalance
            reserve_configurations = self.assets_service.get_reserve_configuraion_data(reserve)
            bonus = reserve_configurations.liquidationBonus
            decimals = reserve_configurations.decimals

            collateral['liquidated_collateral_amount'] = (chosen_debt['debtPrice'] * debtToCover * bonus) / \
                collateral_price * decimals
            
            # max_collateral = atoken_balance * collateral_price * 0.04
            print(f"Max liquidated collateral for reserve {reserve}: {collateral['liquidated_collateral_amount']}")
        
        # Choose the maximum collateral to receive
        chosen_collateral = max(collaterals, key=lambda c: c['liquidated_collateral_amount'])
        collateral_contract = self.assets_service.get_asset(chosen_collateral['reserve'])
        
        return collateral_contract, chosen_collateral['liquidated_collateral_amount'], \
               debt_contract, debtToCover
                        

    def liquidate(self, borrower: str) -> str:
        collateral_contract, liquidated_collateral_amount, debt_contract, debtToCover = \
        self.check_liquidation_profitability(borrower)
        
        # Balance check
        balance = self.assets_service.get_balance(debt_contract)
        if balance < debtToCover:
            print(f"""Not enough funds to liquidate debt.\n
                    Asset address: {debt_contract.address}""")
            return

        allowance = self.assets_service.get_allowance()
        if allowance <= 0:
            approval_hash = self.assets_service.approve(debt_contract, debtToCover)
            # approval_hash = ContractsService.exec_contract(self.account, nonce, 
            #                 debt_asset_contract.functions.approve(LendingPool.address, debtToCover))
        
        
        # liquidatedCollateralAmount = 1 #.toWei(d, 'ether')
        liquidation_func = LendingPool.functions.liquidationCall(
            collateral_contract.address, # Collateral asset
            debt_contract.address, # Debt asset
            borrower, # User to liquidate
            debtToCover, # Amount of debt to cover
            liquidated_collateral_amount, # Amount of collateral to liquidate
            toolkit_.account.address, # Liquidator address
            True # Receive aToken
        )
        nonce = toolkit_.w3.eth.getTransactionCount(toolkit_.account.address)
        liquidation_hash = ContractsService.exec_contract(toolkit_.account, nonce, liquidation_func)

    # def calculate_debt_to_cover(self, user_data: UserData):
    def calculate_debt_to_cover(self, user_reserve_data: UserReserveData):
        debtToCover = math.floor((user_reserve_data.currentStableDebt + user_reserve_data.currentVariableDebt) * \
                        consts.LIQUIDATION_CLOSE_FACTOR)
        # debtToCover2 = math.floor(user_data.currentATokenBalance * consts.LIQUIDATION_CLOSE_FACTOR)
        # TODO: check wei conversion, should use asset and not ether.
        return debtToCover
        # return toolkit_.w3.toWei(debtToCover, 'ether')

    # def estimate_gas():
    #     toolkit_.w3.eth.estimate_gas()
