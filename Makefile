.PHONY: watch

chipstar.pdf: chipstar.tex chipstar.bib relatedWork.tex
	pdflatex chipstar
	bibtex chipstar
	pdflatex chipstar

watch:
	$(shell while true; do inotifywait -e modify *.tex; $(MAKE) chipstar.pdf; done;)


clean:
	rm -f *.aux chipstar.pdf
