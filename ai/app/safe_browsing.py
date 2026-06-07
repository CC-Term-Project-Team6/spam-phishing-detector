import os
import requests
from urlextract import URLExtract
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
SAFE_BROWSING_URL = "https://safebrowsing.googleapis.com/v4/threatMatches:find"


extractor = URLExtract()


def extract_urls(text: str):
    return extractor.find_urls(text)


def check_safe_browsing(text: str):
    urls = extract_urls(text)

    if not urls:
        return {
            "enabled": bool(API_KEY),
            "status": "none",
            "urls": [],
            "matches": []
        }

    if not API_KEY:
        return {
            "enabled": False,
            "status": "unknown",
            "urls": urls,
            "matches": []
        }

    payload = {
        "client": {
            "clientId": "smishing-detector",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url} for url in urls]
        }
    }

    try:
        response = requests.post(
            f"{SAFE_BROWSING_URL}?key={API_KEY}",
            json=payload,
            timeout=5
        )
        response.raise_for_status()

        data = response.json()
        matches = data.get("matches", [])

        if matches:
            return {
                "enabled": True,
                "status": "malicious",
                "urls": urls,
                "matches": matches
            }

        return {
            "enabled": True,
            "status": "clean",
            "urls": urls,
            "matches": []
        }

    except Exception as e:
        return {
            "enabled": False,
            "status": "unknown",
            "urls": urls,
            "matches": [],
            "error": str(e)
        }