## 시스템 구조

**입력 레이어 (파트 A)**

```
이미지 업로드         텍스트 직접 입력
(스크린샷·사진)       (붙여넣기)
        ↓                   ↓
```

**Azure Functions (파트 C)**

```
API 게이트웨이 · 라우팅 · 입력 분기
    ↓ 이미지면              ↓ 텍스트면
Azure AI Vision         그대로 전달
(OCR · 텍스트 추출)
Blob Storage
(이미지 저장)
    ↓ 추출된 텍스트         ↓ 텍스트
    └──────────────────────┘
                ↓ 텍스트만 전달
```

**Container Apps (파트 B)**

```
전처리 파이프라인
  유니코드 정규화 → 이모지 제거 → 문자 치환
  자모 복원 → URL 토큰화 → 구두점 복원
        ↓
[1단계] Google Safe Browsing
  악성 URL 탐지 → 즉시 smishing 확정 (신뢰도 0.99)
        ↓ (악성 아닌 경우)
[2단계] 3가지 병렬 실행
  ┌─────────────────────────────────────────┐
  │ Spam 모델                               │
  │ (blockenters/sms-spam-classifier)       │
  │ HuggingFace Transformer                 │
  ├─────────────────────────────────────────┤
  │ Smishing 모델                           │
  │ (Hyeonseo/ko-smishing-detector)         │
  │ sklearn Pipeline (joblib)               │
  ├─────────────────────────────────────────┤
  │ Azure AI Language                       │
  │ 엔티티·URL·전화번호·기관명 감지          │
  └─────────────────────────────────────────┘
        ↓
[3단계] Aggregator — 종합 판정
  우선순위:
  1. Safe Browsing 악성 → smishing / high / 0.99
  2. adjusted_smishing_score ≥ 0.70 → smishing / high
     (smishing 모델 0.7 + Azure 엔티티 점수 0.3 가중합)
  3. spam_score ≥ 0.70 → spam / medium
  4. 이외 → normal / low
        ↓ 결과 JSON 반환
```

**Azure Functions (파트 C) — 결과 처리**

```
Azure SQL 저장          결과 카드 반환
(visibility=public일 때만) (label·risk_level·confidence·reason)
        ↓                       ↓
        └──────────────────────┘
                ↓
```

**프론트엔드 결과 표시 (파트 A)**

```
React · Azure Static Web Apps
(이력 조회 ← Azure SQL)
```
