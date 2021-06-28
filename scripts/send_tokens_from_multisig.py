import sys
from brownie import (interface, accounts)
from ape_safe import ApeSafe

from utils.config import (prompt_bool)

unslashed_covers = [
    {
        "policy_name": "Lido Staking Facilities",
        "premiumToken": "0xfe85E8EA3CB9870Cd70279866e6Bac74DC5730B8"
    },
    {
        "policy_name": "Lido Certus",
        "premiumToken": "0xBB75a91A9b5D97d0A13d43e2fB5EB55DB9572eE1"
    },
    {
        "policy_name": "Lido P2P",
        "premiumToken": "0x5E6a186c5cAD9E0feBbB46f5adeCF5b58933E4aa"
    },
    {
        "policy_name": "Lido ChorusOne",
        "premiumToken": "0xcBCA7868471f77C4950Dd9DE8f7e504D87510BEf"
    },
    {
        "policy_name": "Lido stakefish",
        "premiumToken": "0x4DfBbb24edDBD42DCc98c37db08F9af0e8bd3cD0"
    },
    {
        "policy_name": "Lido Blockspace",
        "premiumToken": "0xa1262165194d287779F59B51482309B86f3c0575"
    },
    {
        "policy_name": "Lido DSRV",
        "premiumToken": "0x1775239dbD793DbafDB4F41862BEBe929794c9C4"
    },
    {
        "policy_name": "Lido Everstake",
        "premiumToken": "0x9725A9B4D54742b9C03C505ADE4BeeEd00ddb73B"
    },
    {
        "policy_name": "Lido SkillZ",
        "premiumToken": "0x6dec89eD7c059862640C9b1365C1f1602bb0Ae92"
    }
]

def main():
    safe_address = '0xD089cc83f5B803993E266ACEB929e52A993Ca2C8'
    safe = ApeSafe(safe_address)
    agent_address = '0x3e40d73eb977dc6a537af587d48316fee66e9c8c'
    should_send = False

    for cover in unslashed_covers:
        request_tokens = interface.ERC20(cover["premiumToken"])
        ut = safe.contract(cover["premiumToken"])

        balance = request_tokens.balanceOf(safe_address)

        if balance > 0:
          print('got tokens', balance, cover["premiumToken"], ut.balanceOf(safe_address))
          ut.transfer(agent_address, balance, {'gas_limit': 100000})
          should_send = True

    safe_tx = safe.multisend_from_receipts()

    print('gas', safe.estimate_gas(safe_tx))

    if not should_send:
      print("nothing to send to agent!")
      return


    print("safe tx preview:")
    safe.preview(safe_tx)

    sys.stdout.write('Are you sure (y/n)? ')

    if not prompt_bool():
        print('Aborting')
        return

    safe.post_transaction(safe_tx)
