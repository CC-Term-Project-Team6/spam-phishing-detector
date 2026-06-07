from app.domain_trust import is_trusted_url


def aggregate_result(spam_result, smishing_result, azure_result, safe_browsing_result):
    # 1단계: Google Safe Browsing에서 악성 URL이면 바로 스미싱 확정
    if safe_browsing_result.get("status") == "malicious":
        return {
            "label": "smishing",
            "risk_level": "high",
            "confidence": 0.99,
            "reasons": ["Google Safe Browsing에서 악성 URL로 탐지됨"]
        }

    spam_score = spam_result["spam_score"]
    smishing_score = smishing_result["smishing_score"]

    reasons = []

    risk_entities = azure_result.get("risk_entities", [])

    entity_score = 0.0

    for entity in risk_entities:
        category = entity["category"]

        if category == "URL":
            url = entity["text"]

            if is_trusted_url(url):
                reasons.append(f"신뢰 도메인 확인: {url} (위험 점수 미반영)")
                continue

            entity_score += 0.4
            reasons.append(f"Azure 위험 엔티티 탐지: URL({url})")

        elif category == "Organization":
            entity_score += 0.2
            reasons.append(f"Azure 위험 엔티티 탐지: 기관명({entity['text']})")

        elif category == "PhoneNumber":
            entity_score += 0.3
            reasons.append(f"Azure 위험 엔티티 탐지: 전화번호({entity['text']})")

    entity_score = min(entity_score, 1.0)

    if risk_entities:
        adjusted_smishing_score = (
            0.7 * smishing_score
            + 0.3 * entity_score
        )
    else:
        adjusted_smishing_score = smishing_score

    adjusted_spam_score = spam_score

    if adjusted_smishing_score >= 0.70:
        label = "smishing"
        risk_level = "high"
        confidence = adjusted_smishing_score
        reasons.append("AI 모델이 스미싱 패턴을 탐지함")

    elif adjusted_spam_score >= 0.70:
        label = "spam"
        risk_level = "medium"
        confidence = adjusted_spam_score
        reasons.append("AI 모델이 스팸 패턴을 탐지함")

    else:
        label = "normal"
        risk_level = "low"
        confidence = 1 - max(adjusted_spam_score, adjusted_smishing_score)
        reasons.append("특별한 위험 신호 없음")

    return {
        "label": label,
        "risk_level": risk_level,
        "confidence": round(confidence, 4),
        "reasons": reasons
    }