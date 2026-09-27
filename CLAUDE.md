# 작업 규칙

## 언어: 항상 한국어

- 사용자에게 보내는 모든 메시지(답변, 진행 상황 안내, 질문, 요약)는 **한국어로만** 작성한다.
- 커밋 메시지, 코드 주석, 문서(README 등), 이슈·PR 본문도 한국어로 작성한다.
- 영어는 고유명사·명령어·파일명·코드·학술 용어 원어 병기처럼 번역하면 오히려 뜻이 달라지는 경우에만,
  한국어 문장 안에서 괄호 등으로 최소한으로 쓴다. 예: 내용타당도 비율(CVR), `latexmk`
- 사용자가 영어로 질문하더라도 한국어로 답한다.

## 저장소 개요

- 박사학위 논문(XeLaTeX + kotex): `thesis.tex`, `chapters/`, `config/`
- VR 검도훈련 콘텐츠 델파이 설문: 문항 원본은 `survey/items.tex` 하나뿐이며
  설문지·논문 부록·분석 스크립트가 모두 이 파일을 사용한다.
- 분석: `analysis/delphi_analysis.py` (테스트: `make test`)
- 빌드: `make` → `thesis.pdf`, `survey/delphi-survey.pdf` (한자 표시에 Noto CJK 글꼴 필요)
