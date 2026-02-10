"""
AI 그림 해석 프로세스 결과 저장용 MongoDB 스키마 및 API 요청/응답 모델.
컬렉션: analysis_logs

모듈 매핑:
- image_to_json: AiMind-AiModels/image_to_json (객체탐지 → 그림 요소 분석)
- json_to_llm: AiMind-AiModels/jsonToLlm (요소 위치/크기 분석 → LLM)
- ocr: AiMind-AiModels/ocr
"""
from datetime import datetime, timezone
from typing import Any

from beanie import Document, Indexed
from pydantic import BaseModel, Field


class AnalysisLog(Document):
    """
    그림 해석 프로세스에서 발생하는 AI 분석 결과 문서.
    MySQL user_id를 기준으로 조회 (외래키처럼 사용).
    """
    user_id: Indexed(int) = Field(..., description="MySQL User ID")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="생성 시각",
    )
    # image_to_json (객체탐지 → 그림 요소 분석) 결과
    image_to_json: dict[str, Any] = Field(default_factory=dict)
    # jsonToLlm (요소 위치/크기 분석) 결과
    json_to_llm_json: dict[str, Any] = Field(default_factory=dict)
    # jsonToLlm 등 그림 해석 LLM 결과 (객체, 선택)
    llm_result_text: dict[str, Any] | None = None
    # ocr 모듈 결과 (선택)
    ocr_json: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "analysis_logs"


# --- API 요청/응답 스키마 ---


class AnalysisSaveRequest(BaseModel):
    """POST /analysis/save 요청 바디."""
    user_id: int = Field(..., description="MySQL User ID")
    image_to_json: dict[str, Any] = Field(default_factory=dict)
    json_to_llm_json: dict[str, Any] = Field(default_factory=dict)
    llm_result_text: dict[str, Any] | None = None
    ocr_json: dict[str, Any] = Field(default_factory=dict)


class AnalysisLogResponse(BaseModel):
    """분석 로그 한 건 응답 (JSON 리스트 항목)."""
    id: str
    user_id: int
    created_at: datetime
    image_to_json: dict[str, Any]
    json_to_llm_json: dict[str, Any]
    llm_result_text: dict[str, Any] | None
    ocr_json: dict[str, Any]

    class Config:
        from_attributes = True
