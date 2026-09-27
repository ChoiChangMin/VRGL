# 박사학위 논문 (LaTeX)

XeLaTeX + kotex 기반 한국어 박사학위 논문 템플릿입니다.
GitHub에 푸시하면 **GitHub Actions가 자동으로 PDF를 빌드**합니다.

## 폴더 구조

```
thesis.tex              메인 파일 (장 순서 조정)
config/metadata.tex     ★ 제목·저자·지도교수·학과·연도 등 논문 정보
config/preamble.tex     패키지, 글꼴, 여백, 줄간격 등 서식
frontmatter/            표지, 인준지, 국문/영문 초록, 감사의 글
chapters/               본문 각 장 (01-서론 ~ 05-결론, 부록)
figures/                그림 파일 (PDF/PNG)
references.bib          참고문헌 (BibTeX)
survey/items.tex        ★ 델파이 설문 문항 (설문지·논문 부록 공통 원본)
survey/survey-config.tex  설문 차수, 회신 기한, 연락처, 표시 옵션
survey/delphi-survey.tex  전문가 배포용 설문지
survey/REVIEW.md        설문지 검토·개선 사항 및 확인 필요 항목
analysis/               델파이 응답 분석 스크립트 (CVR, 합의도, 수렴도, CV)
```

## 사용 방법

1. `config/metadata.tex` 에서 논문 정보를 수정합니다.
2. `chapters/` 의 각 파일에 본문을 작성합니다. 장을 추가하려면 파일을 만들고 `thesis.tex` 에 `\input{...}` 을 추가합니다.
3. Zotero·Mendeley·Google Scholar 에서 BibTeX 을 내보내 `references.bib` 에 붙여넣고 `\cite{키}` 로 인용합니다.
4. 커밋 후 푸시하면 PDF가 빌드됩니다.

### 자주 쓰는 기능

| 기능 | 사용법 |
|---|---|
| 교차 참조 | `\label{fig:x}` 후 `\cref{fig:x}` → "그림 3.1" |
| 인용 | `\cite{knuth1984texbook}` |
| 작성 메모 | `\todo{보완 필요}` → 여백에 표시 (최종본은 `\def\FinalVersion{}` 로 숨김) |
| 정리/정의 | `theorem`, `lemma`, `definition`, `proof` 환경 |
| 알고리즘 | `algorithm` 환경 (algorithm2e) |

## 델파이 설문 조사

문항은 `survey/items.tex` **한 곳에서만** 관리합니다. 수정하면 배포용 설문지(`survey/delphi-survey.pdf`)와
논문 부록 A가 함께 바뀌고, 분석 스크립트도 같은 문항 번호를 사용합니다.

```bash
python analysis/delphi_analysis.py template -o data/round1.csv            # 응답 입력 양식 (엑셀로 열기)
python analysis/delphi_analysis.py analyze data/round1.csv --round 1 --survey-stats
```

분석하면 `analysis/output/round1-results.tex` 가 생겨 논문 4장에 결과 표가 자동으로 들어가고,
`survey/round1-stats.tex` 가 생겨 2차 설문지(`\DelphiRound{2}`)에 1차 결과 열이 자동으로 표시됩니다.
개선 사항과 확인이 필요한 항목은 [`survey/REVIEW.md`](survey/REVIEW.md) 를 참고하세요.

## PDF 받기

- **매 푸시마다:** 저장소의 **Actions** 탭 → 최신 실행 → 하단 *Artifacts* 의 `thesis-pdf` 다운로드 (논문 + 설문지)
- **버전 배포 (지도교수 제출용 등):** 태그를 푸시하면 **Releases** 에 PDF가 첨부됩니다.
  ```bash
  git tag v0.1-draft && git push origin v0.1-draft
  ```

## 진행 관리

Issues → New issue 에서 템플릿을 사용할 수 있습니다.
- **장(Chapter) 작성 작업** — 장별 진행 체크리스트
- **지도교수/심사위원 피드백** — 받은 피드백을 항목별로 기록하고 반영 여부 추적

## 로컬 빌드 (선택)

TeX Live, 나눔 글꼴, Noto CJK 글꼴(한자용)이 설치되어 있다면:

```bash
make          # thesis.pdf + survey/delphi-survey.pdf 생성
make watch    # 저장할 때마다 자동 빌드
make clean    # 빌드 파일 삭제
```

Overleaf 를 쓰려면 저장소를 zip 으로 올리고 *Menu → Compiler* 를 **XeLaTeX** 로 설정하세요.

## 학교 양식 맞추기

대학원마다 표지·인준지·여백·줄간격 규정이 다릅니다.
`frontmatter/titlepage.tex`, `frontmatter/approval.tex`, `config/preamble.tex` 의 `geometry`/`setspace` 설정을 학교 규정에 맞게 수정하세요.
