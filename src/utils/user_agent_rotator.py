thonimport logging
import random
from typing import Iterable, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENTS: List[str] = [
    # A small, diverse set of realistic desktop & mobile user agents.
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_0) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
]

class UserAgentRotator:
    """
    Randomly picks User-Agent strings from a configurable pool.
    """

    def __init__(self, custom_agents: Optional[Iterable[str]] = None) -> None:
        self._agents: List[str] = list(custom_agents) if custom_agents else list(
            DEFAULT_USER_AGENTS
        )
        if not self._agents:
            # Defensive: revert to default pool if given empty list
            self._agents = list(DEFAULT_USER_AGENTS)
        logger.info("UserAgentRotator initialized with %d user agents.", len(self._agents))

    def get_user_agent(self) -> str:
        """
        Return a random user agent string from the pool.
        """
        ua = random.choice(self._agents)
        logger.debug("Selected User-Agent: %s", ua)
        return ua