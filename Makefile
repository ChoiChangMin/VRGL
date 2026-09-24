.PHONY: all watch clean count

all:            ## PDF 빌드
	latexmk thesis.tex

watch:          ## 저장할 때마다 자동 빌드
	latexmk -pvc thesis.tex

clean:          ## 빌드 산출물 삭제
	latexmk -C

count:          ## 장별 단어/글자 수
	@for f in chapters/*.tex; do printf "%-35s " $$f; texcount -brief -merge $$f 2>/dev/null | head -1; done
