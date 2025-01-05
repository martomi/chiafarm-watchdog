# std
import re
import logging
import dateutil.parser
from dataclasses import dataclass
import datetime
from typing import List


@dataclass
class WalletPeakMessage:
    peak: int  # Wallet peak at logline
    peak_time: datetime.datetime  # peak datetime
    log_time: datetime.datetime  # log line datetime


class WalletPeakParser:
    """This class can parse info log messages from the chia wallet

    You need to have enabled "log_level: INFO" in your chia config.yaml
    The chia config.yaml is usually under ~/.chia/mainnet/config/config.yaml

    Example log line:
    2023-01-31T12:56:41.725 wallet chia.wallet.wallet_blockchain: INFO     Peak set to: 3183522 timestamp: 1675162567
    """

    def __init__(self):
        logging.debug("Enabled parser for wallet activity - peak age.")
        self._regex = re.compile(
            r"([0-9:.T\-\+]*)"
            r" (?:[-0-9a-zA-Z.]+ )?wallet (?:src|chia)\.wallet\.wallet_blockchain(?:\s*)?: INFO\s+"
            r"Peak set to: ([0-9]+) timestamp: ([0-9]+)"
        )

    def parse(self, logs: str) -> List[WalletPeakMessage]:
        """Parses wallet peak activity messages from a bunch of logs

        :param logs: String of logs - can be multi-line
        :returns: A list of parsed messages - can be empty
        """

        parsed_messages = []
        matches = self._regex.findall(logs)
        for match in matches:
            peak = int(match[1])

            log_time = dateutil.parser.parse(match[0])
            # The log_time may or may not be TZ aware based on Chia version.
            # Peak timestamps are always UTC but we need a TZ aware time if the log time is TZ aware
            if log_time.tzinfo is None or log_time.tzinfo.utcoffset(log_time) is None:
                tz = None
            else:
                tz = datetime.timezone.utc
            peak_time = datetime.datetime.fromtimestamp(int(match[2]), tz=tz)

            parsed_messages.append(WalletPeakMessage(peak=peak, peak_time=peak_time, log_time=log_time))
        return parsed_messages
