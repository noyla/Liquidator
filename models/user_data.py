USER_RESERVE_DATA = ['currentATokenBalance', 'currentStableDebt',
                     'currentVariableDebt', 'principalStableDebt',
                     'scaledVariableDebt', 'stableBorrowRate',
                     'liquidityRate', 'stableRateLastUpdated',
                     'usageAsCollateralEnabled']
class UserData:
    def __init__(self, currentATokenBalance, currentStableDebt, currentVariableDebt,
    principalStableDebt, scaledVariableDebt, stableBorrowRate, liquidityRate, 
    stableRateLastUpdated, usageAsCollateralEnabled: bool) -> None:
        self.currentATokenBalance = currentATokenBalance
        self.currentStableDebt = currentStableDebt
        self.currentVariableDebt = currentVariableDebt
        self.principalStableDebt = principalStableDebt
        self.scaledVariableDebt = scaledVariableDebt
        self.stableBorrowRate = stableBorrowRate
        self.liquidityRate = liquidityRate
        self.stableRateLastUpdated = stableRateLastUpdated
        self.usageAsCollateralEnabled = usageAsCollateralEnabled

    @staticmethod
    def from_raw_list(user_data: list):
        return UserData(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4],
        user_data[5], user_data[6], user_data[7], user_data[8])
        
