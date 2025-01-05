# std
import re
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List

# lib
from dateutil import parser as dateutil_parser


@dataclass
class BlockMessage:
    """Parsed information from full node logs"""

    timestamp: datetime
    blocks_count: int


class BlockParser:
    """This class can parse info log messages from the chia farmer

    You need to have enabled "log_level: INFO" in your chia config.yaml
    The chia config.yaml is usually under ~/.chia/mainnet/config/config.yaml
    """

    def __init__(self):
        logging.debug("Enabled parser for block found stats.")
        self._regex = re.compile(
            r"([0-9:.]*) (?:[-0-9a-zA-Z.]+ )?full_node (?:src|chia).full_node.full_node\s*: INFO\s* ((?:🍀 ️|.)\s*Farmed unfinished_block)"
        )

    def parse(self, logs: str) -> List[BlockMessage]:
        """Parses all farmer activity messages from a bunch of logs

        :param logs: String of logs - can be multi-line
        :returns: A list of parsed messages - can be empty
        """

        parsed_messages = []
        matches = self._regex.findall(logs)
        for match in matches:
            parsed_messages.append(BlockMessage(timestamp=dateutil_parser.parse(match[0]), blocks_count=1))

        return parsed_messages
