# """
# Ledger Service – Payment Round Execution

# This module contains the core business logic for executing a "round" of payments
# in the ledger system. It is responsible for:

#     • Loading and normalizing price and balance data from persistent JSON files.
#     • Calculating total cost for a given set of participants.
#     • Selecting the next payer based on configured tie-breaking strategies.
#     • Updating account balances to reflect the transaction.
#     • Appending transaction records to the persistent history log.

# All monetary values are stored internally as Decimal for precision, and are
# serialized to floats for JSON compatibility when returning results to the API.
# """

# from decimal import Decimal
# from typing import List, Dict, Tuple
# from storage.json_store import load_json, save_json
# from storage.history_store import append_history_row, read_history
# from utils.money import D, money
# from utils.tie_strategies import select_payer
# from utils.time_utils import now_iso
# from config import PRICES_FILE, BALANCES_FILE, HISTORY_FILE


# def normalize_prices(raw: Dict[str, float]) -> Dict[str, Decimal]:
#     """
#     Convert raw price mappings into normalized Decimal values.

#     Args:
#         raw (dict[str, float]): Dictionary of participant names to price values.

#     Returns:
#         dict[str, Decimal]: Normalized prices with currency precision applied.
#     """
#     return {name: money(D(value)) for name, value in raw.items()}


# def normalize_balances(raw: Dict[str, float]) -> Dict[str, Decimal]:
#     """
#     Convert raw balance mappings into normalized Decimal values.

#     Args:
#         raw (dict[str, float]): Dictionary of participant names to balance values.

#     Returns:
#         dict[str, Decimal]: Normalized balances with currency precision applied.
#     """
#     return {name: money(D(value)) for name, value in raw.items()}


# def compute_total_cost(prices: Dict[str, Decimal], people: List[str]) -> Tuple[Decimal, List[str]]:
#     """
#     Calculate total cost for a list of participants, filtering out unknown names.

#     Args:
#         prices (dict[str, Decimal]): Mapping of participants to their price values.
#         people (list[str]): List of participant names to consider.

#     Returns:
#         tuple:
#             total (Decimal): Sum of prices for included participants (rounded to currency).
#             included (list[str]): Subset of names that exist in the price list.
#     """
#     included = [p for p in people if p in prices]
#     total = sum((prices[p] for p in included), start=Decimal("0"))
#     return money(total), included


# def run_round(people: List[str], tie_strategy: str) -> Dict:
#     """
#     Execute a payment round: determine payer, update balances, and record history.

#     Args:
#         people (list[str]):
#             List of participants to include in this round.
#             If empty, defaults to all participants with configured prices.
#         tie_strategy (str):
#             Name of the tie-breaking strategy to use when multiple participants
#             are equally eligible to be the payer. Must be one of the supported
#             strategies in `utils.tie_strategies.select_payer`.

#     Raises:
#         ValueError: If none of the provided participants match configured prices.

#     Returns:
#         dict: Updated ledger state after the round execution, including:
#             - timestamp (str): ISO 8601 timestamp of round execution.
#             - payer (str): Selected participant responsible for paying.
#             - total_cost (float): Total amount for this round.
#             - included (list[str]): Participants included in the calculation.
#             - tie (str): Tie-breaking strategy used.
#             - prices (dict[str, float]): Updated prices for all participants.
#             - balances (dict[str, float]): Updated balances after transaction.
#             - history (list): Full transaction history from the ledger.
#     """
#     # Load data and normalize to Decimal values for precision-safe calculations
#     prices = normalize_prices(load_json(PRICES_FILE, {}))
#     balances = normalize_balances(load_json(BALANCES_FILE, {}))

#     # Default to all participants if none provided
#     if not people:
#         people = list(prices.keys())

#     # Calculate total cost and ensure valid participants
#     total_cost, included = compute_total_cost(prices, people)
#     if not included:
#         raise ValueError("No provided people match prices")

#     # Select the participant who will pay this round
#     payer = select_payer(
#         balances, included, tie_strategy, read_history(HISTORY_FILE)
#     )

#     # Debit each included participant for their price
#     for participant in included:
#         balances[participant] = money(balances[participant] - prices[participant])

#     # Credit the selected payer with the total round amount
#     balances[payer] = money(balances[payer] + total_cost)

#     # Persist updated balances to JSON storage (floats for JSON compatibility)
#     save_json(BALANCES_FILE, {k: float(v) for k, v in balances.items()})

#     # Record transaction in history log
#     timestamp = now_iso()
#     append_history_row(HISTORY_FILE, timestamp, payer, total_cost, included)

#     # Return updated ledger state for API consumption
#     return {
#         "timestamp": timestamp,
#         "payer": payer,
#         "total_cost": float(total_cost),
#         "included": included,
#         "tie": tie_strategy,
#         "prices": {k: float(v) for k, v in prices.items()},
#         "balances": {k: float(v) for k, v in balances.items()},
#         "history": read_history(HISTORY_FILE),
#     }
