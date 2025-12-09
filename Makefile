.PHONY: watch

chipstar.pdf: chipstar.tex chipstar.bib
	pdflatex chipstar
	pdflatex chipstar
	pdflatex chipstar

watch:
	$(shell while true; do inotifywait -e modify *.tex; $(MAKE) chipstar.pdf; done;)


clean:
	rm -f \
		chipstar.aux \
		chipstar.acn \
		chipstar.alg \
		chipstar.blg \
		chipstar.glg \
		chipstar.glo \
		chipstar.gls \
		chipstar.ist \
		chipstar.log \
		chipstar.out \
		chipstar.pdf
