thonimport argparse
import json
import logging
import os
import sys
from typing import Any, Dict

# Ensure local imports work when running as a script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from extractors.facebook_parser import FacebookHashtagScraper  # type: ignore[import]
from utils.proxy_manager import ProxyManager  # type: ignore[import]
from utils.user_agent_rotator import UserAgentRotator  # type: ignore[import]

def load_json_file(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

def resolve_path(base_dir: str, path: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.abspath(os.path.join(base_dir, path))

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape public Facebook posts for a given hashtag."
    )
    parser.add_argument(
        "--config",
        "-c",
        default=os.path.join(os.path.dirname(CURRENT_DIR), "data", "input.example.json"),
        help="Path to JSON config file (default: data/input.example.json)",
    )
    parser.add_argument(
        "--settings",
        "-s",
        default=os.path.join(CURRENT_DIR, "config", "settings.json"),
        help="Path to settings JSON file (default: src/config/settings.json)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()
    setup_logging(verbose=args.verbose)
    logger = logging.getLogger("main")

    try:
        config = load_json_file(args.config)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error(f"Failed to load config file: {exc}")
        sys.exit(1)

    try:
        settings = load_json_file(args.settings)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error(f"Failed to load settings file: {exc}")
        sys.exit(1)

    hashtag = config.get("hashtag")
    if not hashtag:
        logger.error("Config must contain a non-empty 'hashtag' field.")
        sys.exit(1)

    max_pages = int(config.get("max_pages", 1))
    output_path = config.get("output_file") or os.path.join(
        os.path.dirname(CURRENT_DIR), "data", "output.sample.json"
    )
    output_path = resolve_path(os.getcwd(), output_path)

    proxy_list = config.get("proxies") or []
    proxy_manager = ProxyManager(proxy_list=proxy_list)
    user_agent_rotator = UserAgentRotator(custom_agents=config.get("user_agents"))

    logger.info(
        "Starting Facebook hashtag scraper for #%s (max_pages=%s)", hashtag, max_pages
    )

    scraper = FacebookHashtagScraper(
        hashtag=hashtag,
        max_pages=max_pages,
        settings=settings,
        proxy_manager=proxy_manager,
        user_agent_rotator=user_agent_rotator,
    )

    try:
        posts = scraper.run()
    except KeyboardInterrupt:
        logger.warning("Scraping interrupted by user.")
        sys.exit(1)
    except Exception as exc:
        logger.exception(f"Unexpected error during scraping: {exc}")
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=4)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error(f"Failed to write output file: {exc}")
        sys.exit(1)

    logger.info("Scraping complete. %d posts saved to %s", len(posts), output_path)

if __name__ == "__main__":
    main()