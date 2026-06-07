import os
from dotenv import load_dotenv
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

AZURE_LANGUAGE_ENDPOINT = os.getenv("AZURE_LANGUAGE_ENDPOINT")
AZURE_LANGUAGE_KEY = os.getenv("AZURE_LANGUAGE_KEY")


def get_client():
    if not AZURE_LANGUAGE_ENDPOINT or not AZURE_LANGUAGE_KEY:
        return None

    return TextAnalyticsClient(
        endpoint=AZURE_LANGUAGE_ENDPOINT,
        credential=AzureKeyCredential(AZURE_LANGUAGE_KEY)
    )


def analyze_entities(text: str): # NER
    client = get_client()

    if client is None:
        return {
            "enabled": False,
            "entities": [],
            "risk_entities": []
        }

    try:
        result = client.recognize_entities([text])[0]

        entities = []
        risk_entities = []

        for entity in result.entities:
            item = {
                "text": entity.text,
                "category": entity.category,
                "confidence": round(entity.confidence_score, 4)
            }
            entities.append(item)

            if entity.category in ["URL", "Organization", "PhoneNumber"]:
                risk_entities.append(item)

        return {
            "enabled": True,
            "entities": entities,
            "risk_entities": risk_entities
        }

    except Exception as e:
        return {
            "enabled": False,
            "error": str(e),
            "entities": [],
            "risk_entities": []
        }