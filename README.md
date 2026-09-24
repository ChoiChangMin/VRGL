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

## PDF 받기

- **매 푸시마다:** 저장소의 **Actions** 탭 → 최신 실행 → 하단 *Artifacts* 의 `thesis-pdf` 다운로드
- **버전 배포 (지도교수 제출용 등):** 태그를 푸시하면 **Releases** 에 PDF가 첨부됩니다.
  ```bash
  git tag v0.1-draft && git push origin v0.1-draft
  ```

## 진행 관리

Issues → New issue 에서 템플릿을 사용할 수 있습니다.
- **장(Chapter) 작성 작업** — 장별 진행 체크리스트
- **지도교수/심사위원 피드백** — 받은 피드백을 항목별로 기록하고 반영 여부 추적

## 로컬 빌드 (선택)

TeX Live 와 나눔 글꼴이 설치되어 있다면:

```bash
make          # thesis.pdf 생성
make watch    # 저장할 때마다 자동 빌드
make clean    # 빌드 파일 삭제
```

Overleaf 를 쓰려면 저장소를 zip 으로 올리고 *Menu → Compiler* 를 **XeLaTeX** 로 설정하세요.

## 학교 양식 맞추기

대학원마다 표지·인준지·여백·줄간격 규정이 다릅니다.
`frontmatter/titlepage.tex`, `frontmatter/approval.tex`, `config/preamble.tex` 의 `geometry`/`setspace` 설정을 학교 규정에 맞게 수정하세요.
