# XeLaTeX + biber 로 빌드
$pdf_mode = 5;           # xelatex
$bibtex_use = 2;         # biber 실행
$xelatex = 'xelatex -interaction=nonstopmode -halt-on-error -file-line-error -synctex=1 %O %S';
@default_files = ('thesis.tex');
$clean_ext = 'bbl run.xml synctex.gz xdv';
