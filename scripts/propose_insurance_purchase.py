import os
import sys
from brownie import network, accounts, Wei, interface
from utils.evm_script import encode_call_script

from utils.config import (
    lido_dao_voting_address,
    lido_dao_token_manager_address,
    lido_dao_finance_address,
    ldo_token_address,
    steth_token_address,
    gas_price,
    get_is_live,
    get_deployer_account,
    prompt_bool
)


EMPTY_CALLSCRIPT = '0x00000001'


def create_vote(voting, token_manager, vote_desc, evm_script, tx_params):
    new_vote_script = encode_call_script([(
        voting.address,
        voting.newVote.encode_input(
            evm_script if evm_script is not None else EMPTY_CALLSCRIPT,
            vote_desc,
            False,
            False
        )
    )])
    tx = token_manager.forward(new_vote_script, tx_params)
    vote_id = tx.events['StartVote']['voteId']
    return (vote_id, tx)


def propose_insurance_purchase(
    insurance_purchaser,
    ldo_amount,
    steth_amount,
    insurance_amount,
    reference,
    tx_params
):
    voting = interface.Voting(lido_dao_voting_address)
    token_manager = interface.TokenManager(lido_dao_token_manager_address)
    finance = interface.Finance(lido_dao_finance_address)

    payment_script = encode_call_script([
        (
            finance.address,
            finance.newImmediatePayment.encode_input(
                ldo_token_address,
                insurance_purchaser.address,
                ldo_amount,
                reference
            )
        ),
        (
            finance.address,
            finance.newImmediatePayment.encode_input(
                steth_token_address,
                insurance_purchaser.address,
                steth_amount,
                reference
            )
        ),
        (
            insurance_purchaser.address,
            insurance_purchaser.purchase.encode_input(
                insurance_amount
            )
        )
    ])

    return create_vote(
        voting=voting,
        token_manager=token_manager,
        vote_desc=f'Send {ldo_amount} tokens at {ldo_token_address} to {insurance_purchaser.address}: {reference}',
        evm_script=payment_script,
        tx_params=tx_params
    )


def main():
    is_live = get_is_live()
    deployer = get_deployer_account(True)

    if 'INSURANCE_PURCHASER_ADDRESS' not in os.environ:
        raise EnvironmentError('Please set the INSURANCE_PURCHASER_ADDRESS env variable')

    insurance_purchaser_address = os.environ['INSURANCE_PURCHASER_ADDRESS']
    insurance_amount = Wei('56.25 ether')
    ldo_amount = Wei('50000 ether')
    steth_amount = Wei('12 ether')
    reference = "Purchase for slashing insurance"

    print(f"You're going to propose sending {ldo_amount} LDO token-wei and {steth_amount} stETH token-wei to {insurance_purchaser_address} to purchase for slashing insurance (reference: '{reference}').")
    sys.stdout.write('Are you sure (y/n)? ')

    if not prompt_bool():
        print('Aborting')
        return

    insurance_purchaser = InsurancePurchaser(insurance_purchaser_address)

    vote_id = propose_insurance_purchase(
        insurance_purchaser=insurance_purchaser,
        ldo_amount=ldo_amount,
        steth_amount=steth_amount,
        insurance_amount=insurance_amount,
        reference=reference,
        tx_params={"from": deployer, "gas_price": Wei(gas_price), "required_confs": 1}
    )[0]

    print('Vote ID:', vote_id)