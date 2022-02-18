import os
import consts
from toolkit import Toolkit

class LiquidationService:
    def __init__(self):
        self.account = Toolkit.w3.eth.account.privateKeyToAccount(
            os.environ.get("ACCOUNT1_PRIVATE_KEY"))
        # self.aave =

    def can_liquidate(user: str) -> bool:
        return True

    def liquidate(self, borrower: str, debtToCover: int):
        pass

    def calculate_debt_to_cover(borrower_user_data: dict):
        debtToCover = (borrower_user_data['currentStableDebt'] + borrower_user_data['currentVariableDebt']) * \
                      consts.LIQUIDATION_CLOSE_FACTOR
        debtToCover = Toolkit.w3.toWei(1, 'ether')

