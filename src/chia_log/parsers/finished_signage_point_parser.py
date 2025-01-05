# std
import re
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List

# lib
from dateutil import parser as dateutil_parser


@dataclass
class FinishedSignagePointMessage:
    """Parsed information from full node logs"""

    timestamp: datetime
    signage_point: int


class FinishedSignagePointParser:
    """This class can parse info log messages from the chia harvester

    You need to have enabled "log_level: INFO" in your chia config.yaml
    The chia config.yaml is usually under ~/.chia/mainnet/config/config.yaml
    """

    def __init__(self):
        logging.debug("Enabled parser for finished signage points.")
        # Doing some "smart" tricks with this expression to also match the 64th signage point
        # with the same regex expression. See test examples to see how they differ.
        self._regex = re.compile(
            r"([0-9:.]*) (?:[-0-9a-zA-Z.]+ )?full_node (?:src|chia).full_node.full_node(?:\s?): INFO\s*(?:⏲️|.)[a-z A-Z,]* ([0-9]*)\/64"
        )

    def parse(self, logs: str) -> List[FinishedSignagePointMessage]:
        """Parses all harvester activity messages from a bunch of logs

        :param logs: String of logs - can be multi-line
        :returns: A list of parsed messages - can be empty
        """

        parsed_messages = []
        matches = self._regex.findall(logs)
        for match in matches:
            parsed_messages.append(
                FinishedSignagePointMessage(timestamp=dateutil_parser.parse(match[0]), signage_point=int(match[1]))
            )

        return parsed_messages
