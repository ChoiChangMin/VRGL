# XeLaTeX + biber 로 빌드 (논문 + 델파이 설문지)
$pdf_mode = 5;           # xelatex
$bibtex_use = 2;         # biber 실행
$do_cd = 1;              # 각 파일의 폴더에서 컴파일 (survey/ 상대경로 유지)
$xelatex = 'xelatex -interaction=nonstopmode -halt-on-error -file-line-error -synctex=1 %O %S';
@default_files = ('thesis.tex', 'survey/delphi-survey.tex');
$clean_ext = 'bbl run.xml synctex.gz xdv';
