import sys

from brownie import (
    accounts,
    interface,
    Wei,
    ZERO_ADDRESS
)

from utils.config import (
    ldo_token_address,
    steth_token_address
)

from utils.evm_script import encode_call_script

def main():
    lido = interface.Lido(steth_token_address)
    lido.submit(ZERO_ADDRESS, {"from": accounts[2], "value": "10 ether"})
    lido.submit(ZERO_ADDRESS, {"from": accounts[3], "value": "10 ether"})

    steth_token = interface.ERC20(steth_token_address)
    steth_token.transfer(accounts[0], Wei("10 ether"), {"from": accounts[2]})
    steth_token.transfer(accounts[0], Wei("10 ether"), {"from": accounts[3]})

    ldo_token = interface.ERC20(ldo_token_address)
    ldo_whale = accounts.at("0x454f11d58e27858926d7a4ece8bfea2c33e97b13", force=True)
    ldo_token.transfer(accounts[0], Wei("50000 ether"), {"from": ldo_whale})


