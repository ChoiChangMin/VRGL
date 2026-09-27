#!/usr/bin/env python3
"""델파이 조사 응답 분석 (표준 라이브러리만 사용).

문항 목록은 survey/items.tex 에서 읽어오므로 설문지와 항상 일치합니다.

사용법
  # 1) 응답 입력용 CSV 양식 생성 (엑셀에서 열어 응답 입력)
  python analysis/delphi_analysis.py template -o data/round1.csv

  # 2) 분석: 문항별 통계 CSV, 논문용 LaTeX 표, 다음 차수 설문지용 통계 파일 생성
  python analysis/delphi_analysis.py analyze data/round1.csv --round 1 -o analysis/output

  # 3) 2차 분석 시 1차 응답을 함께 주면 안정도(변이계수 변화량)도 계산
  python analysis/delphi_analysis.py analyze data/round2.csv --round 2 --prev data/round1.csv

산출 지표
  M, SD            평균, 표준편차(표본)
  Mdn, Q1, Q3      중앙값, 사분위수 (SPSS 와 동일한 방식)
  CVR              내용타당도 비율 (Lawshe, 1975): 4점 이상 응답을 '필수'로 간주
  합의도           1 - (Q3 - Q1) / Mdn                      (기준 ≥ .75)
  수렴도           (Q3 - Q1) / 2                            (기준 ≤ .50)
  CV               변이계수 SD / M (안정도)                 (기준 ≤ .50)
"""
from __future__ import annotations

import argparse
import csv
import re
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS_TEX = ROOT / "survey" / "items.tex"

# Lawshe(1975) 최소 CVR (단측 p=.05). 표에 없는 N 은 그보다 작은 가장 가까운 N 의 값(보수적)을 사용
LAWSHE_MIN_CVR = {5: .99, 6: .99, 7: .99, 8: .75, 9: .78, 10: .62, 11: .59, 12: .56,
                  13: .54, 14: .51, 15: .49, 20: .42, 25: .37, 30: .33, 35: .31, 40: .29}

ESSENTIAL_FROM = 4          # 이 점수 이상을 '필수(적절)' 응답으로 간주 (CVR 계산)
MIN_CONSENSUS = 0.75
MAX_CONVERGENCE = 0.50
MAX_CV = 0.50
DOMAIN_WEIGHT_PREFIX = "W"  # 영역별 중요도(100점 배분) 열: W1..W5


@dataclass
class Item:
    id: str
    name: str
    domain: str
    proposed: bool = False


def load_items(path: Path = ITEMS_TEX) -> tuple[list[Item], dict[str, str]]:
    """items.tex 에서 문항(\\Item, \\NewItem)과 영역(\\Domain)을 순서대로 읽는다."""
    text = "\n".join(l.split("%", 1)[0] for l in path.read_text(encoding="utf-8").splitlines())
    items: list[Item] = []
    domains: dict[str, str] = {}
    current = ""
    pattern = re.compile(r"\\(Domain|NewItem|Item|EndDomain)\b(?:\{([^{}]*)\}\{((?:[^{}]|\{[^{}]*\})*)\})?")
    for m in pattern.finditer(text):
        kind, num, name = m.groups()
        name = (name or "").replace("\\&", "&")
        if kind == "Domain":
            current = num
            domains[num] = re.sub(r"\s*\(.*\)$", "", name)
        elif kind == "EndDomain":
            items.append(Item(f"D{current}", "영역 전체 구성", current))
        else:
            items.append(Item(num, name, current, proposed=(kind == "NewItem")))
    return items, domains


def min_cvr(n: int) -> float:
    eligible = [k for k in LAWSHE_MIN_CVR if k <= n]
    return LAWSHE_MIN_CVR[max(eligible)] if eligible else 1.0


def quartiles(xs: list[float]) -> tuple[float, float, float]:
    if len(xs) < 2:
        return xs[0], xs[0], xs[0]
    q1, q2, q3 = statistics.quantiles(xs, n=4, method="exclusive")  # SPSS HAVERAGE 와 동일
    return q1, q2, q3


@dataclass
class Stat:
    item: Item
    n: int
    mean: float
    sd: float
    q1: float
    mdn: float
    q3: float
    cvr: float
    consensus: float
    convergence: float
    cv: float
    cv_prev: float | None = None

    @property
    def criteria(self) -> dict[str, bool]:
        return {"CVR": self.cvr >= min_cvr(self.n),
                "합의도": self.consensus >= MIN_CONSENSUS,
                "수렴도": self.convergence <= MAX_CONVERGENCE,
                "CV": self.cv <= MAX_CV}

    @property
    def passed(self) -> bool:
        return all(self.criteria.values())


def describe(item: Item, xs: list[float]) -> Stat:
    n = len(xs)
    mean = statistics.fmean(xs)
    sd = statistics.stdev(xs) if n > 1 else 0.0
    q1, mdn, q3 = quartiles(xs)
    ne = sum(x >= ESSENTIAL_FROM for x in xs)
    return Stat(item, n, mean, sd, q1, mdn, q3,
                cvr=(ne - n / 2) / (n / 2),
                consensus=1 - (q3 - q1) / mdn if mdn else 0.0,
                convergence=(q3 - q1) / 2,
                cv=sd / mean if mean else 0.0)


def read_responses(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def column(rows: list[dict[str, str]], key: str) -> list[float]:
    out = []
    for r in rows:
        v = (r.get(key) or "").strip()
        if v:
            x = float(v)
            if key[0].isdigit() or key.startswith("D"):
                if not 1 <= x <= 5:
                    raise ValueError(f"{key} 열에 1~5 범위를 벗어난 값: {v} (응답자 {r.get('expert_id')})")
            out.append(x)
    return out


def analyze(rows, items, prev_rows=None) -> list[Stat]:
    stats = []
    for it in items:
        xs = column(rows, it.id)
        if not xs:
            continue
        s = describe(it, xs)
        if prev_rows:
            pxs = column(prev_rows, it.id)
            if len(pxs) > 1:
                s.cv_prev = describe(it, pxs).cv
        stats.append(s)
    return stats


def domain_weights(rows, domains) -> dict[str, float]:
    means = {}
    for d in domains:
        xs = column(rows, f"{DOMAIN_WEIGHT_PREFIX}{d}")
        if xs:
            means[d] = statistics.fmean(xs)
    total = sum(means.values())
    return {d: v / total for d, v in means.items()} if total else {}


# ----------------------------------------------------------------- 출력
def f2(x: float) -> str:
    return f"{x:.2f}"


def write_csv(stats: list[Stat], path: Path) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["번호", "구성요소", "신규제안", "N", "M", "SD", "Q1", "Mdn", "Q3",
                    "CVR", "최소CVR", "합의도", "수렴도", "CV", "이전CV", "CV변화", "판정", "미충족 기준"])
        for s in stats:
            fails = [k for k, ok in s.criteria.items() if not ok]
            w.writerow([s.item.id, s.item.name, "Y" if s.item.proposed else "", s.n,
                        f2(s.mean), f2(s.sd), f2(s.q1), f2(s.mdn), f2(s.q3),
                        f2(s.cvr), f2(min_cvr(s.n)), f2(s.consensus), f2(s.convergence), f2(s.cv),
                        "" if s.cv_prev is None else f2(s.cv_prev),
                        "" if s.cv_prev is None else f2(abs(s.cv - s.cv_prev)),
                        "채택" if s.passed else "검토", " ".join(fails)])


def tex_escape(s: str) -> str:
    return s.replace("&", r"\&").replace("%", r"\%").replace("#", r"\#")


def write_latex_table(stats: list[Stat], domains: dict[str, str], rnd: int, path: Path) -> None:
    """논문 본문/부록에 \\input 할 수 있는 longtable (booktabs 필요)."""
    n = stats[0].n if stats else 0
    lines = [
        f"% delphi_analysis.py 가 생성한 파일 — 직접 수정하지 마세요 ({rnd}차, N={n})",
        r"{\small\setlength{\tabcolsep}{3.5pt}",
        r"\begin{longtable}{llrrrrrrrc}",
        rf"\caption{{{rnd}차 델파이 조사 결과 (N={n}, 최소 CVR={min_cvr(n):.2f})}}\label{{tab:delphi-round{rnd}}}\\",
        r"\toprule",
        r"번호 & 구성요소 & $M$ & $SD$ & $Mdn$ & CVR & 합의도 & 수렴도 & CV & 판정 \\ \midrule \endfirsthead",
        r"\toprule",
        r"번호 & 구성요소 & $M$ & $SD$ & $Mdn$ & CVR & 합의도 & 수렴도 & CV & 판정 \\ \midrule \endhead",
        r"\bottomrule",
        r"\multicolumn{10}{l}{\footnotesize 판정: ○ 모든 기준 충족, △ 일부 미충족(굵게 표시). "
        rf"합의도 $\geq$ {MIN_CONSENSUS:.2f}, 수렴도 $\leq$ {MAX_CONVERGENCE:.2f}, CV $\leq$ {MAX_CV:.2f}. "
        r"$^\dagger$ 연구자 추가 제안 문항.} \\",
        r"\endlastfoot",
    ]
    current = None
    for s in stats:
        if s.item.domain != current:
            current = s.item.domain
            if s is not stats[0]:
                lines.append(r"\midrule")
            lines.append(rf"\multicolumn{{10}}{{l}}{{\textbf{{{current}. {tex_escape(domains.get(current, ''))}}}}} \\")
        c = s.criteria

        def mark(val: str, ok: bool) -> str:
            return val if ok else rf"\textbf{{{val}}}"
        name = tex_escape(s.item.name) + (r"$^\dagger$" if s.item.proposed else "")
        lines.append(" & ".join([
            s.item.id, name, f2(s.mean), f2(s.sd), f2(s.mdn),
            mark(f2(s.cvr), c["CVR"]), mark(f2(s.consensus), c["합의도"]),
            mark(f2(s.convergence), c["수렴도"]), mark(f2(s.cv), c["CV"]),
            "○" if s.passed else "△"]) + r" \\")
    lines += [r"\end{longtable}}", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_survey_stats(stats: list[Stat], rnd: int, path: Path) -> None:
    """다음 차수 설문지에 이전 차수 결과 열을 채우는 파일 (survey/roundN-stats.tex)."""
    lines = [f"% {rnd}차 델파이 결과 — delphi_analysis.py 가 생성 (다음 차수 설문지에서 자동 사용)"]
    for s in stats:
        lines.append(rf"\SetPrevStat{{{s.item.id}}}{{{s.mdn:.1f}}}{{{s.q1:.1f}}}{{{s.q3:.1f}}}{{{s.cvr:.2f}}}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_summary(stats: list[Stat], weights: dict[str, float], domains: dict[str, str]) -> None:
    n = stats[0].n if stats else 0
    print(f"응답자 N={n}, 최소 CVR={min_cvr(n):.2f} (Lawshe, 1975)")
    print(f"{'번호':<7}{'M':>6}{'SD':>6}{'Mdn':>6}{'CVR':>7}{'합의도':>7}{'수렴도':>7}{'CV':>6}  판정")
    for s in stats:
        fails = [k for k, ok in s.criteria.items() if not ok]
        verdict = "채택" if s.passed else "검토(" + ",".join(fails) + ")"
        print(f"{s.item.id:<7}{s.mean:6.2f}{s.sd:6.2f}{s.mdn:6.1f}{s.cvr:7.2f}"
              f"{s.consensus:9.2f}{s.convergence:9.2f}{s.cv:6.2f}  {verdict}")
    rejected = [s.item.id for s in stats if not s.passed]
    print(f"\n채택 {len(stats) - len(rejected)}개 / 검토 필요 {len(rejected)}개: {', '.join(rejected) or '없음'}")
    if weights:
        print("\n영역별 상대적 중요도 (100점 배분 평균 → 가중치)")
        for d, w in weights.items():
            print(f"  {d}. {domains.get(d, ''):<28} {w:6.1%}")


# ----------------------------------------------------------------- CLI
def cmd_template(args) -> None:
    items, domains = load_items()
    header = ["expert_id", "field"] + [it.id for it in items] + [f"{DOMAIN_WEIGHT_PREFIX}{d}" for d in domains]
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerow(header)
    print(f"{out} 생성: 문항 {len(items)}개 + 영역 가중치 {len(domains)}개 열")


def cmd_analyze(args) -> None:
    items, domains = load_items()
    rows = read_responses(Path(args.responses))
    prev = read_responses(Path(args.prev)) if args.prev else None
    missing = [it.id for it in items if it.id not in rows[0]]
    if missing:
        print(f"경고: 응답 파일에 없는 문항 {', '.join(missing)} (분석에서 제외)", file=sys.stderr)
    stats = analyze(rows, items, prev)
    weights = domain_weights(rows, domains)

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    write_csv(stats, out / f"round{args.round}-results.csv")
    write_latex_table(stats, domains, args.round, out / f"round{args.round}-results.tex")
    stats_file = (ROOT / "survey" if args.survey_stats else out) / f"round{args.round}-stats.tex"
    write_survey_stats(stats, args.round, stats_file)
    print_summary(stats, weights, domains)
    print(f"\n출력: {out}/round{args.round}-results.csv, .tex  |  설문지용: {stats_file}")


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description="델파이 조사 응답 분석")
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("template", help="응답 입력용 CSV 양식 생성")
    t.add_argument("-o", "--output", default="data/round1.csv")
    t.set_defaults(func=cmd_template)
    a = sub.add_parser("analyze", help="응답 분석")
    a.add_argument("responses", help="응답 CSV (행: 전문가, 열: 문항 번호)")
    a.add_argument("--round", type=int, default=1)
    a.add_argument("--prev", help="이전 차수 응답 CSV (안정도 계산용)")
    a.add_argument("-o", "--output", default="analysis/output")
    a.add_argument("--survey-stats", action="store_true",
                   help="다음 차수 설문지용 통계를 survey/ 에 저장 (설문지에 이전 차수 결과 열이 자동 표시됨)")
    a.set_defaults(func=cmd_analyze)
    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
