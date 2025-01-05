# std
import re
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List

# lib
from dateutil import parser as dateutil_parser


@dataclass
class HarvesterActivityMessage:
    """Parsed information from harvester logs"""

    timestamp: datetime
    eligible_plots_count: int
    challenge_hash: str
    found_proofs_count: int
    search_time_seconds: float
    total_plots_count: int


class HarvesterActivityParser:
    """This class can parse info log messages from the chia harvester

    You need to have enabled "log_level: INFO" in your chia config.yaml
    The chia config.yaml is usually under ~/.chia/mainnet/config/config.yaml
    """

    def __init__(self):
        logging.debug("Enabled parser for harvester activity - eligible plot events.")
        self._regex = re.compile(
            r"([0-9:.]*) (?:[-0-9a-zA-Z.]+ )?harvester (?:src|chia).harvester.harvester(?:\s?): INFO\s*([0-9]+) plots were "
            r"eligible for farming ([0-9a-z.]*) Found ([0-9]) proofs. Time: ([0-9.]*) s. "
            r"Total ([0-9]*) plots"
        )

    def parse(self, logs: str) -> List[HarvesterActivityMessage]:
        """Parses all harvester activity messages from a bunch of logs

        :param logs: String of logs - can be multi-line
        :returns: A list of parsed messages - can be empty
        """

        parsed_messages = []
        matches = self._regex.findall(logs)
        for match in matches:
            parsed_messages.append(
                HarvesterActivityMessage(
                    timestamp=dateutil_parser.parse(match[0]),
                    eligible_plots_count=int(match[1]),
                    challenge_hash=match[2],
                    found_proofs_count=int(match[3]),
                    search_time_seconds=float(match[4]),
                    total_plots_count=int(match[5]),
                )
            )

        return parsed_messages
