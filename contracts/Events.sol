pragma solidity ^0.6.12;


event FlashLiquidationCall(address debtAsset, uint256 amount, address collateralAsset, uint256 bonus, address user, bool receiveaToken);
event FlashLoanGranted(address asset, uint256 amount, address user);
event LiquidationSuccess(address asset, address collateralAsset, uint256 amountToLiquidate, address user);
event LiquidationFailed(address debtAsset, address collateralAsset, uint256 amountToLiquidate, address user);
event FlashLoanRedeemed(address asset, uint amountOwed, address user);
event FlashLoanError();