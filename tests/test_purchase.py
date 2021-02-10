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
        "0x746d94f1161C991675Ede99aBCDb0412a4fEE43E",
        deployer=deployer
    )

    steth_token.transfer(insurance_purchaser, Wei("3 ether"), {"from": steth_whale})
    ldo_token.transfer(insurance_purchaser, Wei("2000 ether"), {"from": ldo_whale})

    print('steth balance', steth_token.balanceOf(insurance_purchaser))
    # tx = insurance_purchaser.purchase(Wei("2 ether"))
    tx = insurance_purchaser.fail({"from": deployer})
    print(tx.events)

    # assert unslashed_token.balanceOf(deployer) > 0

