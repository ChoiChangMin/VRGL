.PHONY: all watch clean count test

all:            ## PDF 빌드
	latexmk

watch:          ## 저장할 때마다 자동 빌드
	latexmk -pvc thesis.tex

test:           ## 델파이 분석 스크립트 테스트
	python3 -m unittest discover -s analysis

clean:          ## 빌드 산출물 삭제
	latexmk -C

count:          ## 장별 단어/글자 수
	@for f in chapters/*.tex; do printf "%-35s " $$f; texcount -brief -merge $$f 2>/dev/null | head -1; done
