// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

// import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/math/SafeMath.sol";
import "openzeppelin-solidity/contracts/utils/math/SafeMath.sol";
// import "openzeppelin-solidity/contracts/utils/math/SafeERC20.sol";
// import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/IERC20.sol";
// import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/SafeERC20.sol";
import {IFlashLoanReceiver, ILendingPoolAddressesProvider, ILendingPool, IERC20  } from "./Interfaces.sol";
// import { Withdrawable } from "./utils/Withrawable.sol";
import { SafeERC20} from "./Libraries.sol";
// import "./IFlashLoanReceiver.sol";
// import "./ILendingPoolAddressesProvider.sol";
// import "../utils/Withdrawable.sol";

abstract contract FlashLoanReceiverBase is IFlashLoanReceiver{ //, Withdrawable {

    using SafeERC20 for IERC20;
    using SafeMath for uint256;

    address constant ethAddress = 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE;
    ILendingPoolAddressesProvider public addressesProvider;

    constructor(address _addressProvider) {
        addressesProvider = ILendingPoolAddressesProvider(_addressProvider);
    }

    receive() payable external {}

    // function transferFundsBackToPoolInternal(address _reserve, uint256 _amount) internal {
    //     address payable core = addressesProvider.getLendingPoolCore();
    //     transferInternal(core, _reserve, _amount);
    // }

    function transferInternal(address payable _destination, address _reserve, uint256 _amount) internal {
        if(_reserve == ethAddress) {
            (bool success, ) = _destination.call{value: _amount}("");
            require(success == true, "Couldn't transfer ETH");
            return;
        }
        IERC20(_reserve).safeTransfer(_destination, _amount);
    }

    function getBalanceInternal(address _target, address _reserve) internal view returns(uint256) {
        if(_reserve == ethAddress) {
            return _target.balance;
        }
        return IERC20(_reserve).balanceOf(_target);
    }
}