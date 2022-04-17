pragma solidity ^0.6.6;

import "https://github.com/aave/flashloan-box/blob/Remix/contracts/aave/FlashLoanReceiverBase.sol";
import "https://github.com/aave/flashloan-box/blob/Remix/contracts/aave/ILendingPoolAddressesProvider.sol";
import "https://github.com/aave/flashloan-box/blob/Remix/contracts/aave/ILendingPool.sol";

import "./Liquidator.sol";
import "./Events.sol";

contract FlashLiquidator is FlashLoanReceiverBase {
    ILendingPoolAddressesProvider public addressProvider;
    ILiquidator public liquidatorContract;

    constructor(address _addressProvider, address _liquidatorAddress) FlashLoanReceiverBase(_addressProvider) public {
        addressProvider = ILendingPoolAddressesProvider(_addressProvider);
        liquidatorContract = ILiquidator(_liquidatorAddress);
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
        (address memory collateralAsset, uint256 bonus, address memory user, bool memory receiveaToken) = 
        abi.decode(params, (address, uint256, address, bool));

        emit FlashLoanGranted(_assets[0], _amounts[0], user);
        
        // Verify the funds were received
        require(amounts[0] <= getBalanceInternal(address(this), _reserve), "Invalid balance, was the FlashLoan successful?");
        
        // Get LendingPool instance
        // ILendingPool lendingPool = ILendingPool(addressProvider.getLendingPool());
        // Liquidator theLiquidator = Liquidator(lendingPool);
        // theLiquidator.flashLiquidate(address(lendingPool));
        uint256 amountToLiquidate = amounts[0] * bonus;
        address lendingPoolAddress = addressProvider.getLendingPool();
        bool success = liquidatorContract.flashLiquidate(lendingPoolAddress, collateralAsset, assets[0] /* The debt asset to cover */, 
        user, amountToLiquidate, receiveaToken);
    
        // At the end of your logic above, this contract owes
        // the flashloaned amounts + premiums.
        // Therefore ensure your contract has enough to repay
        // these amounts.
        if (!success) {
            emit LiquidationFailed(_assets[0], collateralAsset, amountToLiquidate, user);
            return false;
        }
        
        emit LiquidationSuccess(_assets[0], collateralAsset, amountToLiquidate, user);

        // Approve the LendingPool contract allowance to *pull* the owed amount
        // i.e. AAVE V2's way of repaying the flash loan
        uint amountOwed = 0;
        for (uint i = 0; i < assets.length; i++) {
            amountOwed = amounts[i].add(premiums[i]);
            IERC20(assets[i]).approve(lendingPoolAddress, amountOwed);
            // IERC20(assets[i]).approve(address(LENDING_POOL), amountOwed);
        }

        emit FlashLoanRedeemed(assets[0], amountOwed, user);

        return true;
    }

    /**
        Flash loan 1000000000000000000 wei (1 ether) worth of `_asset`
     */
    function flashLoanCall(address _collateralAsset, address _debtAsset, uint256 _amount, uint256 _bonus, address _user, 
    bool _receiveaToken) public onlyOwner {
        
        emit FlashLiquidationCall(_debtAsset, _amount, _collateralAsset, 
                        _bonus, _user, _receiveaToken);

        address[] memory assets = [_debtAsset];
        uint256[] memory amounts = [_amount];
        // uint256[] amounts = 1 ether;
        uint256[] modes = [0]; // No Debt - return loan at the end of the transaction.
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
    function rugPull() public payable onlyOwner {
        
        // withdraw all ETH
        msg.sender.call{ value: address(this).balance }("");
        
        // withdraw all x ERC20 tokens
        IERC20(kovanAave).transfer(msg.sender, IERC20(kovanAave).balanceOf(address(this)));
        IERC20(kovanDai).transfer(msg.sender, IERC20(kovanDai).balanceOf(address(this)));
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