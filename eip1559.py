from web3 import Web3
from functools import reduce

""" DOCS:
https://web3py.readthedocs.io/en/stable/web3.eth.html#web3.eth.Eth.send_transaction
https://web3py.readthedocs.io/en/stable/web3.eth.html#web3.eth.Eth.fee_history

"""

""" MODES:
Mode = nb and values of percentiles retrieved from a block.
Example: [25, 50, 75] = retrieves the 3 txns at 25%, 50%, 75%
percentiles of the block (txns are in ascending order, weighted by gas used).
'maxPriorityFeePerGas' is calculated by averaging the priority fee (tip)
paid by users during the n last picked txns (n = nb_txns retrieved by block * nb_blocks).
Feel free to change the default modes!
"""
MODE = {
    "slow": [10, 20, 30, 40, 50],  # <1min
    "normal": [10, 30, 50, 70, 90],  # <30sec
    "fast": [50, 60, 70, 80, 90],  # <10sec
}


def estimate_gas_fees(w3: Web3, speed="normal", nb_blocks=3):
    if speed not in MODE:
        raise ValueError("Invalid speed")

    # baseFee: Set by blockchain, varies at each block, always burned
    base_fee = w3.eth.get_block('pending').baseFeePerGas

    # next baseFee: Overestimation of baseFee in next block, difference always refunded
    next_base_fee = base_fee * 2

    # priorityFee: Set by user, tip/reward paid directly to miners, never returned
    reward_history = w3.eth.fee_history(
        nb_blocks, 'pending', MODE[speed])['reward']
    rewards = reduce(lambda x, y: x + y, reward_history)
    avg_reward = sum(rewards) // len(rewards)

    # Estimations: maxFee - (maxPriorityFee + baseFee actually paid) = Returned to used
    return {"maxPriorityFeePerGas": avg_reward,
            "maxFeePerGas": avg_reward + next_base_fee}

    # Merge to your txn to easily get gas fees: txn |= eip1559.estimate_gas_fees(w3)
