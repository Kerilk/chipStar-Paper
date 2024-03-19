.PHONY: watch

chipstar.pdf: chipstar.tex chipstar.bib
	pdflatex chipstar
	bibtex chipstar
	pdflatex chipstar

watch:
	$(shell while true; do inotifywait -e modify chipstar.tex; $(MAKE) chipstar.pdf; done;)


