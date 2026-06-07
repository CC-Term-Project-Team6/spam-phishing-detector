from fastapi import FastAPI
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.preprocessing import preprocess_text
from app.model import predict_spam
from app.azure_language import analyze_entities
from app.aggregator import aggregate_result
import logging
import asyncio
from app.smishing_model import predict_smishing
from app.safe_browsing import check_safe_browsing

app = FastAPI(title="Spam/Phishing Detection AI Service")

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


@app.get("/")
def root():
    return {"message": "AI service is running"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):

    clean_text = preprocess_text(req.text)

    # 1단계: Safe Browsing 먼저 검사
    safe_browsing_result = await asyncio.to_thread(
        check_safe_browsing,
        req.text
    )

    # 2단계: malicious URL이면 모델 추론 없이 바로 최종 판정
    if safe_browsing_result.get("status") == "malicious":
        final_result = aggregate_result(
            spam_result=None,
            smishing_result=None,
            azure_result={"enabled": True, "entities": [], "risk_entities": []},
            safe_browsing_result=safe_browsing_result
        )

        logger.info(
            f"""
[ANALYZE RESULT]
request_id={req.request_id}

clean_text={clean_text}

safe_browsing_result={safe_browsing_result}

final_result={final_result}
"""
        )

        return AnalyzeResponse(
            request_id=req.request_id,
            label=final_result["label"],
            risk_level=final_result["risk_level"],
            confidence=final_result["confidence"],
            reason=final_result["reasons"],
        )

    # 3단계: malicious가 아니면 모델/Azure 병렬 실행
    spam_task = asyncio.to_thread(
        predict_spam,
        clean_text
    )

    smishing_task = asyncio.to_thread(
        predict_smishing,
        clean_text
    )

    azure_task = asyncio.to_thread(
        analyze_entities,
        req.text
    )

    spam_result, smishing_result, azure_result = await asyncio.gather(
        spam_task,
        smishing_task,
        azure_task
    )

    # 4단계: 최종 aggregation
    final_result = aggregate_result(
        spam_result=spam_result,
        smishing_result=smishing_result,
        azure_result=azure_result,
        safe_browsing_result=safe_browsing_result
    )

    logger.info(
        f"""
[ANALYZE RESULT]
request_id={req.request_id}

clean_text={clean_text}

spam_result={spam_result}

smishing_result={smishing_result}

azure_result={azure_result}

safe_browsing_result={safe_browsing_result}

final_result={final_result}
"""
    )

    return AnalyzeResponse(
        request_id=req.request_id,
        label=final_result["label"],
        risk_level=final_result["risk_level"],
        confidence=final_result["confidence"],
        reason=final_result["reasons"],
    )