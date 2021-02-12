from brownie import (
    InsurancePurchaser,
    Wei
)

def test_purchase(
    steth_token,
    ldo_token,
    unslashed_token,
    deployer,
    steth_whale,
    ldo_whale
):
    steth_to_eth_max_slippage = 100 # 1%
    ldo_to_steth_max_slippage = 400 # 4%

    insurance_purchaser = InsurancePurchaser.deploy(
        steth_to_eth_max_slippage,
        ldo_to_steth_max_slippage,
        {"from": deployer},
    )

    steth_token.transfer(insurance_purchaser, Wei("10 ether"), {"from": steth_whale})
    ldo_token.transfer(insurance_purchaser, Wei("50000 ether"), {"from": ldo_whale})

    print('steth balance before', steth_token.balanceOf(insurance_purchaser))
    print('ldo balance before', ldo_token.balanceOf(insurance_purchaser))

    tx = insurance_purchaser.purchase(Wei("56.25 ether"), Wei("70 ether"), {"from": deployer})

    print('unslashed_token afterall', unslashed_token.balanceOf(deployer))

    assert unslashed_token.balanceOf(deployer) > Wei("70 ether")
