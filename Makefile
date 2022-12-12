all: install_requirements makemessages

.PHONY: install_requirements
install_requirements:
	pipenv requirements > postcode_lookup/requirements.txt

.PHONY: i18n
i18n_extract:
	pybabel extract -F ./babel.cfg -o /tmp/_messages.pot postcode_lookup/
	pybabel update -i /tmp/_messages.pot -d postcode_lookup/locale/

.PHONY: i18n_compile
i18n_compile:
	pybabel compile -f -d postcode_lookup/locale/
