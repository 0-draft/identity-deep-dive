PYTHON ?= python3

.PHONY: install collect normalize score report-daily report-weekly update weekly

install:
	$(PYTHON) -m pip install -r requirements.txt

collect:
	$(PYTHON) scripts/collect.py

normalize:
	$(PYTHON) scripts/normalize.py

score:
	$(PYTHON) scripts/score.py

report-daily:
	$(PYTHON) scripts/report.py --mode daily

report-weekly:
	$(PYTHON) scripts/report.py --mode weekly

update: collect normalize score report-daily

weekly: collect normalize score report-weekly
