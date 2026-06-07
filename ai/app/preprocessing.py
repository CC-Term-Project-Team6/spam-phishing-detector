import re
import unicodedata


def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def tokenize_url(text: str) -> str:
    return re.sub(r"https?://\S+|www\.\S+", "__URL__", text)


def remove_noise(text: str) -> str:
    text = re.sub(r"[^\w\s가-힣ㄱ-ㅎㅏ-ㅣ._]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def preprocess_text(text: str) -> str:
    text = normalize_unicode(text)
    text = tokenize_url(text)
    text = remove_noise(text)
    return text
