from utils.evm_script import encode_call_script

from brownie import (
    interface,
    InsurancePurchaser,
    Wei
)

from utils.config import (
    lido_dao_voting_address,
    lido_dao_token_manager_address,
    lido_dao_finance_address,
    ldo_token_address,
    steth_token_address,
)


def main():
    insurance_purchaser = InsurancePurchaser.at("0x...")
    voting = interface.Voting(lido_dao_voting_address)
    token_manager = interface.TokenManager(lido_dao_token_manager_address)
    finance = interface.Finance(lido_dao_finance_address)

    ldo_amount = Wei('50000 ether')
    steth_amount = Wei('13 ether')
    insurance_amount = Wei('56.25 ether')
    reference = "Purchase for slashing insurance"

    purchase_script = encode_call_script([
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

    print(purchase_script)


