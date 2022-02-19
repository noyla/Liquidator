RESERVE_CONFIGURATION_DATA = ['decimals', 'ltv', 'liquidationThreshold', 'liquidationBonus',
                              'reserveFactor', 'usageAsCollateralEnabled', 'borrowingEnabled',
                              'stableBorrowRateEnabled', 'isActive', 'isFrozen']

class ReserveConfigurationData:
    def __init__(self, currentATokenBalance, currentStableDebt, currentVariableDebt, 
                principalStableDebt, scaledVariableDebt, stableBorrowRate,
                liquidityRate, stableRateLastUpdated, usageAsCollateralEnabled):
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
            res[RESERVE_CONFIGURATION_DATA[i]] = v
        
        return ReserveConfigurationData(list(res.values))