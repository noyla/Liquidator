// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import { IERC20, ILendingPoolAddressesProvider, ILendingPool } from "./Interfaces.sol";
// import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
// import "./Interfaces.sol";

// import "./ILendingPoolAddressesProvider.sol";
// import "./ILendingPool.sol";
// import "https://github.com/aave/flashloan-box/blob/Remix/contracts/aave/ILendingPoolAddressesProvider.sol";
// import "https://github.com/aave/flashloan-box/blob/Remix/contracts/aave/ILendingPool.sol";

interface ILiquidator {
    function flashLiquidate(address _lendingPoolAddress, address _collateral, address _debtReserve,
        address _user, uint256 _purchaseAmount, bool _receiveaToken) external returns (bool);
}

contract Liquidator {
    // address public lendingPoolAddressProvider;
    // ILendingPool public lendingPool;
    
    // constructor(address _lendingPoolAddressProvider) public {
    // constructor(ILendingPool _lendingPool) public {
    // constructor() public {
    // }

    function flashLiquidate(
        address _lendingPoolAddress,
        address _collateral, 
        address _debtReserve,
        address _user,
        uint256 _purchaseAmount,
        bool _receiveaToken
    )
        external
        returns (bool)
    {        
        // Approve the lending pool to spend `_purchaseAmount` of `_debtReserve` so the debt is covered.
        require(IERC20(_debtReserve).approve(_lendingPoolAddress, _purchaseAmount), "Approval error");
        
        // Liquidate
        ILendingPool lendingPool = ILendingPool(_lendingPoolAddress);
        // _purchaseAmount = uint(-1);
        lendingPool.liquidationCall(_collateral, _debtReserve, _user, type(uint256).max, 
                                    _receiveaToken);
        
        return true;
    }

    function liquidate(
        address _lendingPoolAddressProvider,
        address _collateral, 
        address _debtReserve,
        address _user,
        uint256 _purchaseAmount,
        bool _receiveaToken
    )
        external
        returns (bool)
    {
        // Get lending pool
        ILendingPoolAddressesProvider addressProvider = ILendingPoolAddressesProvider(_lendingPoolAddressProvider);
        ILendingPool lendingPool = ILendingPool(addressProvider.getLendingPool());
        
        // Approve the liquidated amount
        require(IERC20(_debtReserve).approve(address(lendingPool), _purchaseAmount), "Approval error");

        // Assumes this contract already has `_purchaseAmount` of `_reserve`.
        lendingPool.liquidationCall(_collateral, _debtReserve, _user, type(uint256).max /*_purchaseAmount*/, 
                                    _receiveaToken);
        
        return true;
    }
}