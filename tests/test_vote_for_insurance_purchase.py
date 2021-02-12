from brownie import Wei, InsurancePurchaser
from scripts.propose_insurance_purchase import propose_insurance_purchase


dao_holders = [
    '0x3e40d73eb977dc6a537af587d48316fee66e9c8c',
    '0xb8d83908aab38a159f3da47a59d84db8e1838712',
    '0xa2dfc431297aee387c05beef507e5335e684fbcd',
    '0x1597d19659f3de52abd475f7d2314dcca29359bd',
    '0x695c388153bea0fbe3e1c049c149bad3bc917740',
    '0x945755de7eac99008c8c57bda96772d50872168b',
    '0xad4f7415407b83a081a0bee22d05a8fdc18b42da',
    '0xfea88380baff95e85305419eb97247981b1a8eee',
    '0x0f89d54b02ca570de82f770d33c7b7cf7b3c3394',
    '0x9bb75183646e2a0dc855498bacd72b769ae6ced3',
    '0x447f95026107aaed7472a0470931e689f51e0e42',
    '0x1f3813fe7ace2a33585f1438215c7f42832fb7b3',
    '0xc24da173a250e9ca5c54870639ebe5f88be5102d',
    '0xb842afd82d940ff5d8f6ef3399572592ebf182b0',
    '0x91715128a71c9c734cdc20e5edeeea02e72e428e',
    '0x8b1674a617f103897fb82ec6b8eb749ba0b9765b',
    '0x8d689476eb446a1fb0065bffac32398ed7f89165',
    '0x9849c2c1b73b41aee843a002c332a2d16aaab611'
]


def test_vote_for_ldo_transfer(
    steth_token,
    ldo_token,
    unslashed_token,
    dao_voting,
    dao_agent,
    deployer,
    stranger,
    steth_whale,
    ldo_whale,
    accounts
):
    # the DAO are not holding insurance token at the begining
    assert unslashed_token.balanceOf(dao_agent) == 0

    # deploy a proxy contract that will handle purchasing
    insurance_purchaser = InsurancePurchaser.deploy(
        100,
        400,
        {"from": deployer}
    )

    assert insurance_purchaser.owner() == deployer
    insurance_purchaser.transfer_ownership(dao_agent, {"from": deployer})
    assert insurance_purchaser.owner() == dao_agent.address

    insurance_amount = Wei('56.25 ether')
    min_insurance_tokens = Wei('70 ether')
    ldo_amount = Wei('50000 ether')
    steth_amount = Wei('12 ether')

    vote_id = propose_insurance_purchase(
        insurance_purchaser=insurance_purchaser,
        ldo_amount=ldo_amount,
        steth_amount=steth_amount,
        insurance_amount=insurance_amount,
        min_insurance_tokens=min_insurance_tokens,
        reference='Purchase slashing insurance',
        tx_params={'from': dao_holders[0]}
    )[0]

    print('vote_id:', vote_id)

    for holder_addr in dao_holders:
        print('voting from acct:', holder_addr)
        accounts[0].transfer(holder_addr, '0.1 ether')
        account = accounts.at(holder_addr, force=True)
        dao_voting.vote(vote_id, True, False, {'from': account})

    assert dao_voting.canExecute(vote_id)

    tx = dao_voting.executeVote(vote_id, {'from': accounts[0]})
    print(tx.events)

    assert unslashed_token.balanceOf(dao_agent) >= Wei("70 ether")
