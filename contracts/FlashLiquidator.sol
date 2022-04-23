// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

// import "https://github.com/aave/flashloan-box/blob/Remix/contracts/aave/FlashLoanReceiverBase.sol";
// import "https://github.com/aave/flashloan-box/blob/Remix/contracts/aave/ILendingPoolAddressesProvider.sol";
// import "https://github.com/aave/flashloan-box/blob/Remix/contracts/aave/ILendingPool.sol";
// import "openzeppelin-solidity/contracts/utils/math/SafeMath.sol";
import "@OpenZeppelin/contracts/access/Ownable.sol";
import { ILendingPoolAddressesProvider, ILendingPool, IERC20 } from "./Interfaces.sol";
// import "openzeppelin-solidity/contracts/utils/math/SafeMath.sol";
// import {SafeMath} from "./Libraries.sol";
import "./FlashLoanReceiverBase.sol";
// import "./consts.sol";
// import "./Events.sol";
import "./Liquidator.sol";


contract FlashLiquidator is FlashLoanReceiverBase, Ownable {
    event FlashLiquidationCall(address indexed debtAsset, uint256 amount, address indexed collateralAsset, uint256 bonus, address indexed user, bool receiveaToken);
    event FlashLoanGranted(address asset, uint256 amount, address user);
    event LiquidationSuccess(address asset, address collateralAsset, uint256 amountToLiquidate, address user);
    event LiquidationFailed(address debtAsset, address collateralAsset, uint256 amountToLiquidate, address user);
    event FlashLoanRedeemed(address asset, uint amountOwed, address user);
    event FlashLoanError(string reason);
    event UnhandledError(bytes lowLevelData);
    event RugPullSucceed();
    event RugPullFailed();

    ILendingPoolAddressesProvider public addressProvider;
    // ILiquidator public liquidatorContract;

    constructor(address _addressProvider/*, address _liquidatorAddress*/) FlashLoanReceiverBase(_addressProvider) {
        addressProvider = ILendingPoolAddressesProvider(_addressProvider);
        // liquidatorContract = ILiquidator(_liquidatorAddress);
    }

    /**
        This function is called after your contract has received the flash loaned amount
     */
    function executeOperation(
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata premiums,
        address initiator,
        bytes calldata params
    )
        external
        override
        returns (bool)
    {
        //
        // This contract now has the funds requested.
        // Decode liquidation params.
        // 
        (address collateralAsset, uint256 bonus, address user, bool receiveaToken) = 
        abi.decode(params, (address, uint256, address, bool));
        address debtAsset = assets[0];
        uint256 amountToLiquidate = amounts[0];
        uint256 premium = premiums[0];
        emit FlashLoanGranted(debtAsset, amountToLiquidate, user);
        
        // Verify the funds were received
        verifyBalance(amountToLiquidate, debtAsset);
        // require(amountToLiquidate <= getBalanceInternal(address(this), debtAsset), 
        //         "Invalid balance, was the FlashLoan successful?");
        
        // Get LendingPool instance
        // ILendingPool lendingPool = ILendingPool(addressProvider.getLendingPool());
        // Liquidator theLiquidator = Liquidator(lendingPool);
        // theLiquidator.flashLiquidate(address(lendingPool));
        uint256 totalToLiquidate = amountToLiquidate * bonus;
        address lendingPoolAddress = addressProvider.getLendingPool();
        try this.flashLiquidate(lendingPoolAddress, collateralAsset, debtAsset, user, 
        totalToLiquidate, receiveaToken) returns (bool success){
            if (!success) {
                emit LiquidationFailed(debtAsset, collateralAsset, totalToLiquidate, user);
                return false;
            }
            // return success;
        } catch Error(string memory reason) {
            emit FlashLoanError(reason);
            return false;
        }
        catch (bytes memory lowLevelData) {  
            emit UnhandledError(lowLevelData);
            return false;
        }
        // bool success = liquidatorContract.flashLiquidate(lendingPoolAddress, collateralAsset, debtAsset, user, 
        //                                                 totalToLiquidate, receiveaToken);
    
        // At the end of your logic above, this contract owes
        // the flashloaned amounts + premiums.
        // Therefore ensure your contract has enough to repay
        // these amounts.
        // if (!success) {
        //     emit LiquidationFailed(debtAsset, collateralAsset, totalToLiquidate, user);
        //     return false;
        // }
        
        emit LiquidationSuccess(debtAsset, collateralAsset, totalToLiquidate, user);

        // Approve the LendingPool contract allowance to *pull* the owed amount
        // i.e. AAVE V2's way of repaying the flash loan
        // amountOwed = repayFlashLoan(lendingPoolAddress, debtAsset, amounts, premiums);
        uint amountOwed = amountToLiquidate + premium;
        IERC20(debtAsset).approve(lendingPoolAddress, amountToLiquidate + premium);
        // for (uint i = 0; i < assets.length; i++) {
        //     amountOwed = amounts[i] + premiums[i];
        //     IERC20(assets[i]).approve(lendingPoolAddress, amountOwed);
        //     // IERC20(assets[i]).approve(address(LENDING_POOL), amountOwed);
        // }
        emit FlashLoanRedeemed(debtAsset, amountOwed, user);

        return true;
    }

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

    function verifyBalance(uint256 amountToLiquidate, address debtAsset
    )
        private
        view
    {
        require(amountToLiquidate <= getBalanceInternal(address(this), debtAsset), 
                "Invalid balance, was the FlashLoan successful?");
    }

    function repayFlashLoan(address lendingPoolAddress, address debtAsset, uint256[] calldata amounts,
        uint256[] calldata premiums
    ) 
        private 
        returns(uint) 
    {
        uint amountOwed = amounts[0] + premiums[0];
        IERC20(debtAsset).approve(lendingPoolAddress, amountOwed);
        
        return amountOwed;
    }

    /**
        Flash loan 1000000000000000000 wei (1 ether) worth of `_asset`
     */
    function flashLoanCall(address _collateralAsset, address _debtAsset, uint256 _amount, uint256 _bonus, address _user, 
    bool _receiveaToken) public onlyOwner {
        
        emit FlashLiquidationCall(_debtAsset, _amount, _collateralAsset, 
                        _bonus, _user, _receiveaToken);

        address[] memory assets = new address[](1);
        assets[0] = _debtAsset;
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = _amount;
        // uint256[] amounts = 1 ether;
        uint256[] memory modes = new uint256[](1); // No Debt - return loan at the end of the transaction.
        modes[0] = uint256(0); // No Debt - return loan at the end of the transaction.
        address onBehalfOf = address(this);
        uint16 referralCode = 0;
        bytes memory params = abi.encode(_collateralAsset, _bonus, _user, _receiveaToken);
        
        // Proceed to FlashLoan
        ILendingPool lendingPool = ILendingPool(addressProvider.getLendingPool());
        lendingPool.flashLoan(address(this), assets, amounts, modes, onBehalfOf, params, referralCode);
    }

    /*
    * Rugpull all ERC20 tokens from the contract
    */
    function rugPull(address _tokenContract) public payable onlyOwner {
        
        // withdraw all ETH
        (bool sent,) = msg.sender.call{ value: address(this).balance}("");
        if (!sent) {
            emit RugPullFailed();
        }
        address KOVAN_AAVE = 0xB597cd8D3217ea6477232F9217fa70837ff667Af;
        address  KOVAN_DAI = 0xFf795577d9AC8bD7D90Ee22b6C1703490b6512FD;
        address  KOVAN_LINK = 0xAD5ce863aE3E4E9394Ab43d4ba0D80f419F61789;
        
        // withdraw all x ERC20 tokens
        require(IERC20(KOVAN_AAVE).transfer(msg.sender, IERC20(KOVAN_AAVE).balanceOf(address(this))), 
                "Witdhraw of AAVE failed");
        require(IERC20(KOVAN_DAI).transfer(msg.sender, IERC20(KOVAN_DAI).balanceOf(address(this))), 
                "Withdraw of DAI failed");
        
        // Withdraw from the input token address
        IERC20 tokenContract = IERC20(_tokenContract);
        require(tokenContract.transfer(msg.sender, tokenContract.balanceOf(address(this))), 
                "Withdraw failed");
        
        emit RugPullSucceed();
        
        // IERC20(kovanLink).transfer(msg.sender, IERC20(kovanLink).balanceOf(address(this)));
    }

    /*
    * Deposits the flashed AAVE, DAI and LINK liquidity onto the lending pool as collateral
    */
    // function flashDeposit(ILendingPool _lendingPool) public {
        
    //     // approve lending pool
    //     IERC20(kovanDai).approve(lendingPoolAddr, flashDaiAmt1);
    //     IERC20(kovanAave).approve(lendingPoolAddr, flashAaveAmt0);
    //     IERC20(kovanLink).approve(lendingPoolAddr, flashLinkAmt2);
        
    //     // deposit the flashed AAVE, DAI and LINK as collateral
    //     _lendingPool.deposit(kovanDai, flashDaiAmt1, address(this), uint16(0));
    //     _lendingPool.deposit(kovanAave, flashAaveAmt0, address(this), uint16(0));
    //     _lendingPool.deposit(kovanLink, flashLinkAmt2, address(this), uint16(0));
        
    // }
}