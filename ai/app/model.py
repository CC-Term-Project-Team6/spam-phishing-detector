from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

MODEL_NAME = "blockenters/sms-spam-classifier"

tokenizer = None
model = None


def load_model():
    global tokenizer, model

    if tokenizer is None or model is None:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_NAME,
        )
        model.eval()


def predict_spam(text: str):
    load_model()

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)[0]

    normal_score = probs[0].item() + 0.2
    spam_score = probs[1].item() * 0.8

    if spam_score >= normal_score:
        label = "spam"
        confidence = spam_score
    else:
        label = "normal"
        confidence = normal_score

    return {
        "label": label,
        "confidence": round(confidence, 4),
        "spam_score": round(spam_score, 4),
        "normal_score": round(normal_score, 4),
        "model_name": MODEL_NAME
    }