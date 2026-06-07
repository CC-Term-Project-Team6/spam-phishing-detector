import os
import tldextract

BASE_DIR = os.path.dirname(__file__)
TRUSTED_DOMAIN_PATH = os.path.join(BASE_DIR, "trusted_domains.txt")

TRUSTED_SUFFIXES = {"go.kr", "ac.kr"}


def load_trusted_domains():
    try:
        with open(TRUSTED_DOMAIN_PATH, encoding="utf-8") as f:
            return frozenset(
                line.strip()
                for line in f
                if line.strip() and not line.startswith("#")
            )
    except FileNotFoundError:
        return frozenset()


TRUSTED_DOMAINS = load_trusted_domains()


def is_trusted_url(url: str) -> bool:
    ext = tldextract.extract(url)

    if not ext.suffix:
        return False

    registrable_domain = f"{ext.domain}.{ext.suffix}"

    return (
        registrable_domain in TRUSTED_DOMAINS
        or ext.suffix in TRUSTED_SUFFIXES
    )