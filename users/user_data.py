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
        res = {}
        for i, v in enumerate(user_data):
            res[USER_RESERVE_DATA[i]] = v
        
        return UserData(list(res.values))
        
