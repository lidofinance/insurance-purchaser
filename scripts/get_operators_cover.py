from brownie import (
  accounts,
  interface,
  Wei
)

unslashed_covers = [
    {
        "policy_name": "Lido Staking Facilities",
        "damage_eth_covered": 439.75,
        "marketAddress": "0xecCAE88f9d594ba3089d0c03B1C298F546ae99d3",
        "premiumToken": "0xfe85E8EA3CB9870Cd70279866e6Bac74DC5730B8"
    },
    {
        "policy_name": "Lido Certus",
        "damage_eth_covered": 660.5,
        "marketAddress": "0x7F05191abF1ac9A105413A3D203aD96bA401e824",
        "premiumToken": "0xBB75a91A9b5D97d0A13d43e2fB5EB55DB9572eE1"
    },
    {
        "policy_name": "Lido P2P",
        "damage_eth_covered": 770.475,
        "marketAddress": "0xDceae1E433C6bD32681F39B34e1c4E43aa87c680",
        "premiumToken": "0x5E6a186c5cAD9E0feBbB46f5adeCF5b58933E4aa"
    },
    {
        "policy_name": "Lido ChorusOne",
        "damage_eth_covered": 491.75,
        "marketAddress": "0x6b3D669381808C1AA593339f0e2A79e206eD688A",
        "premiumToken": "0xcBCA7868471f77C4950Dd9DE8f7e504D87510BEf"
    },
    {
        "policy_name": "Lido stakefish",
        "damage_eth_covered": 491.75,
        "marketAddress": "0xDDDe61C2a24d7a6961d0B2cE35ae0E767f8E6202",
        "premiumToken": "0x4DfBbb24edDBD42DCc98c37db08F9af0e8bd3cD0"
    },
    {
        "policy_name": "Lido Blockspace",
        "damage_eth_covered": 491.75,
        "marketAddress": "0x2B639aC410B27C52B04d792F359AD443227768cB",
        "premiumToken": "0xa1262165194d287779F59B51482309B86f3c0575"
    },
    {
        "policy_name": "Lido DSRV",
        "damage_eth_covered": 0,
        "marketAddress": "0xb8eF0BE1b7Ff74bFebBED0F8e6E13Ac79D2f20fc",
        "premiumToken": "0x1775239dbD793DbafDB4F41862BEBe929794c9C4"
    },
    {
        "policy_name": "Lido Everstake",
        "damage_eth_covered": 663.025,
        "marketAddress": "0xDE2849C8B3BAAAB590960a899BEa3b7d2ef24d78",
        "premiumToken": "0x9725A9B4D54742b9C03C505ADE4BeeEd00ddb73B"
    },
    {
        "policy_name": "Lido SkillZ",
        "damage_eth_covered": 663.025,
        "marketAddress": "0x4f587155B1a4d958d28b038d4D354e7962bE7Bde",
        "premiumToken": "0x6dec89eD7c059862640C9b1365C1f1602bb0Ae92"
    }
]

def main():
    agent = accounts.at('0x3e40d73eb977dc6a537af587d48316fee66e9c8c', force=True)
    eth_spent = 0

    for cover in unslashed_covers:
        print("Calc cover for ", cover["policy_name"])
        eth_to_cover = cover["damage_eth_covered"]
        um = interface.UnslashedMarket(cover["marketAddress"])
        ut = interface.ERC20(cover["premiumToken"])

        deposit_delta = um.coverToPremiumTokens(eth_to_cover*1e18) * um.premiumTokenPrice18eRatio()/1e18

        print("Cover for", eth_to_cover * 0.05," ETH")
        print("ETH required to make deposit: ", deposit_delta / 1e18)

        premium_balance_before = ut.balanceOf(agent.address)
        um.depositPremium({'from': agent, 'value': deposit_delta})
        premium_balance_after  = ut.balanceOf(agent.address)
        print("Premium tokens delta: ", (premium_balance_after-premium_balance_before)/1e18)
        print("Premium tokens balance after: ", (premium_balance_after)/1e18)
        # print("To address", cover["marketAddress"])
        print("ETH amount", Wei(deposit_delta), deposit_delta/1e18)
        # print("Premium tokens contract", cover["premiumToken"])
        # print("Premium tokens received", Eth(ut.balanceOf("0xD089cc83f5B803993E266ACEB929e52A993Ca2C8")))
        eth_spent += deposit_delta

    print("total ETH spent", eth_spent / 1e18)
