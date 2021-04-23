from brownie import (
    accounts,
    interface,
    Wei
)

def main():
    um = interface.UnslashedMarket('0x746d94f1161C991675Ede99aBCDb0412a4fEE43E')
    ut = interface.ERC20('0x2B76f72BFFcBE386EE6BD5F801f24f472dc9f633')
    agent = accounts.at('0x3e40d73eb977dc6a537af587d48316fee66e9c8c', force=True)
    premium_balance_before = ut.balanceOf(agent.address)
    StETH = interface.ERC20('0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84')
    curve_pool = '0xDC24316b9AE028F1497c275EB9192a3Ea0f67022'
    agent_steth_balance = StETH.balanceOf(agent.address)
    # get all the ETH we can from the insurance fund's StETH
    # we won't do this in the real purchase tx, it's for the ease of calc for now
    StETH.approve(curve_pool, agent_steth_balance, {'from': agent})
    interface.StableSwapSTETH(curve_pool).exchange(1, 0, agent_steth_balance, 0.9*agent_steth_balance, {'from': agent})

    DESIRED_AMOUNT_COVERED = 400000
    CURRENT_AMOUNT_COVERED = 196749

    deposit_delta = um.coverToPremiumTokens((DESIRED_AMOUNT_COVERED-CURRENT_AMOUNT_COVERED) * 0.05) * um.premiumTokenPrice18eRatio()

    print("ETH required to make deposit: ", deposit_delta / 1e18)

    um.depositPremium({'from': agent, 'value': deposit_delta})

    premium_balance_after  = ut.balanceOf(agent.address)
    print("Premium tokens delta: ", (premium_balance_after-premium_balance_before)/1e18)
    print("Premium tokens balance after: ", (premium_balance_after)/1e18)
