from brownie import Wei
from brownie.network.state import Chain

from utils.evm_script import encode_call_script


ONE_MINUTE = 60


def test_happy_path(
    steth_token,
    steth_pool,
    ldo_token,
    unslashed_token,
    dao_voting,
    dao_agent,
    deployer,
    stranger,
    steth_whale,
    ldo_whale,
    purchase_helpers
):
    # deploying and purhchase
    insurance_purchaser = purchase_helpers.deploy_purchaser(
        100,
        500,
        deployer=deployer
    )

    # steth_token.transfer(insurance_purchaser, Wei("1 ether"), {"from": steth_whale})
    ldo_token.transfer(insurance_purchaser, Wei(
        "2000 ether"), {"from": ldo_whale})

    print('steth balance before', steth_token.balanceOf(insurance_purchaser))
    print('ldo balance before', ldo_token.balanceOf(insurance_purchaser))
    tx = insurance_purchaser.purchase(
        Wei("1 ether"), Wei("1.2 ether"), {"from": deployer})

    print(tx.events)
    print('unslashed_token afterall', unslashed_token.balanceOf(deployer))
    assert unslashed_token.balanceOf(deployer) > 0
