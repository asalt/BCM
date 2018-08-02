python ./make_abstract_book.py
xelatex --interaction=nonstopmode ./abstract_book_formatted.tex
xelatex --interaction=nonstopmode ./abstract_book_formatted.tex


python ./make_judging_sheets.py
xelatex --interaction=nonstopmode ./judging_sheets.tex
xelatex --interaction=nonstopmode ./judging_sheets.tex

xelatex --interaction=nonstopmode ./detailed_sheets.tex
xelatex --interaction=nonstopmode ./detailed_sheets.tex
