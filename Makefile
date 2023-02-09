all:
	poetry build
	poetry install

doc:
	cd doc ; mkdocs serve

.PHONY: doc
