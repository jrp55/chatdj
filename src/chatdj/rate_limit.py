from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass
import os

PERIOD_HOURS = int(os.environ.get('RATE_LIMIT_PERIOD_HOURS', '24'))
PERIOD_TIMEDELTA = timedelta(hours=PERIOD_HOURS)
PERIOD_PROCESSING_BYTES = int(os.environ.get('RATE_LIMIT_PROCESSING_BYTES',
                                             50*1024*1024))


@dataclass
class UsageRecord:
    timestamp: datetime
    amount: int = 0


def expire_old_records(amounts: List[UsageRecord],
                       expiry_time: datetime) -> List[UsageRecord]:
    def should_keep(amount: UsageRecord) -> bool:
        return amount.timestamp < expiry_time

    return filter(should_keep, amounts)


class InMemoryRateLimiter(object):
    """
    An in-memory rate limiter to ensure that usage abuse does not occur.
    The service is very cheap to run so we don't massively care about keeping
    strict records across e.g. restarts/redeployments so no need to save usage
    data to files or a database or something.
    """

    def __init__(self):
        self._id_to_amounts: Dict[str, List[UsageRecord]]

    def register_usage(self, user_id: str, bytes_to_register: int) -> bool:
        """
        :param user_id: str ID of user to check rate limit of
        :param bytes_to_register: int Number of bytes to check rate limit
        against
        :return: True if the request is allowed; False if request should not be
        allowed.

        Call with a consistent user ID (e.g. spotify user id) and the amount
        of bytes that are about to be processed. This function will expire any
        out of date usage records and attempt to see if the new amount is
        allowed given the global rate limit amounts.
        """
        current_timestamp = datetime.now()
        amounts = self._id_to_amounts.setdefault(user_id, list())
        expiry_timestamp = current_timestamp - PERIOD_TIMEDELTA
        valid_amounts = expire_old_records(amounts, expiry_timestamp)
        candidate_amount = bytes_to_register + \
            sum(map(lambda x: x.amount, valid_amounts))

        if candidate_amount > PERIOD_PROCESSING_BYTES:
            return False

        valid_amounts.append(UsageRecord(current_timestamp, bytes_to_register))
        self._id_to_amounts[user_id] = valid_amounts
        return True
