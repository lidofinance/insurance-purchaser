import sys

from brownie import (
    network,
    accounts,
    InsurancePurchaser,
    Wei
)

from utils.config import (
    lido_dao_agent_address,
    gas_price,
    get_is_live,
    get_deployer_account,
    prompt_bool
)


def main():
    is_live = get_is_live()
    deployer = get_deployer_account(is_live)

    steth_to_eth_max_slippage = 25 # 0.25%
    ldo_to_steth_max_slippage = 500 # 5%

    print('Deployer:', deployer)
    print('Steth to eth max slippage (10000 bp max):', steth_to_eth_max_slippage)
    print('Ldo to steth max slippage (10000 bp max):', ldo_to_steth_max_slippage)
    print('Gas price:', gas_price)

    sys.stdout.write('Proceed? [y/n]: ')

    if not prompt_bool():
        print('Aborting')
        return

    purchaser = InsurancePurchaser.deploy(
        steth_to_eth_max_slippage,
        ldo_to_steth_max_slippage,
        {"from": deployer},
        publish_source=is_live
    )

    purchaser.transfer_ownership(
        lido_dao_agent_address,
        {"from": deployer, "gas_price": Wei(gas_price), "required_confs": 1}
    )

    print("Done!")
