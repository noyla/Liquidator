import math
import os
from typing import Tuple

from web3 import Web3
from assets_service import AssetsService
import consts
from contracts_service import ContractsService
from toolkit import Toolkit
from pools import LendingPool, PriceOracle
from models.user_data import UserData

class LiquidationService:
    def __init__(self):
        self.account = Toolkit.w3().eth.account.privateKeyToAccount(
            os.environ.get("ACCOUNT1_PRIVATE_KEY"))
        self.assets_service = AssetsService()

    def check_liquidation_profitability(self, borrower: str):# -> Tuple[UserData, Web3.eth.contract]:
        """
        Gets liquidation info of user collaterals.
        Calculating which reserve has the best profit

        Args:
            borrower (str): Borrower user address

        Returns:
            Tuple[UserData, Web3.eth.Eth.contract]: Returns user data and the reserve contract
        """
        # TODO: iterate the assets and call getUserReserveData, check what collateral we have 
        collaterals = self.assets_service.get_user_collateral_assets(borrower)
        if not collaterals:
            print(f"No collateral assets found to liquidate for borrower {borrower}")
            return
        
        # Calculate profitability of liquidationCheck currentATokenBalance
        for collateral in collaterals:
            user_data = collateral.get('userReserveData')
            reserve = collateral.get('reserve')
            asset_contract = self.assets_service.get_asset(reserve)
            price = PriceOracle.functions.getAssetPrice(asset_contract.address).call()
            atoken_balance = user_data.currentATokenBalance
            max_collateral = atoken_balance * price * 0.04
            print(f'Max Collateral for reserve {reserve}: {max_collateral}')

        
        return user_data, reserve
                        

    def liquidate(self, borrower: str) -> str:#, debtToCover: int) -> str:
        user_data, reserve = self.check_liquidation_profitability(borrower)
        reserve = "USDC"
        asset_contract = self.assets_service.get_asset(reserve)
        allowance = 0
        # allowance = asset_contract.functions.allowance(self.account.address, 
        #                                                LendingPool.address).call()
        
        if allowance <= 0:
            user_data = self.assets_service.get_user_reserve_data(asset_contract.address, 
                                                                  borrower)
            debtToCover = self.calculate_debt_to_cover(user_data)
            nonce = Toolkit.w3().eth.getTransactionCount(self.account.address)
            approval_hash = ContractsService.exec_contract(self.account, nonce, 
            asset_contract.functions.approve(LendingPool.address, debtToCover))
        
        # Balance check
        # c = Toolkit.w3().eth.getBalance(liquidator_account.address)
        # balance = aave.functions.balanceOf(liquidator_account.address).call()
        collateral = reserve
        liquidatedCollateralAmount = 1 #.toWei(d, 'ether')
        liquidation_func = LendingPool.functions.liquidationCall(
            collateral,
            asset_contract.address,
            borrower,
            debtToCover, # Toolkit.w3().toWei(amountAave * AAVE_ETHER_CONVERSION, 'ether'),
            liquidatedCollateralAmount,
            self.account.address,
            True # Receive aToken
        )
        nonce = Toolkit.w3().eth.getTransactionCount(self.account.address)
        liquidation_hash = ContractsService.exec_contract(self.account, nonce, liquidation_func)

    def calculate_debt_to_cover(self, user_data: UserData):
        debtToCover = math.floor((user_data.currentStableDebt + user_data.currentVariableDebt) * \
                        consts.LIQUIDATION_CLOSE_FACTOR)
        debtToCover2 = math.floor(user_data.currentATokenBalance * consts.LIQUIDATION_CLOSE_FACTOR)
        # TODO: check wei conversion, should use asset and not ether.
        return debtToCover
        # return Toolkit.w3().toWei(debtToCover, 'ether')

