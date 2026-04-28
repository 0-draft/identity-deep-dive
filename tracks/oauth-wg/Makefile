PYTHON ?= python3

.PHONY: install collect normalize score report-daily report-weekly prune update weekly

install:
	$(PYTHON) -m pip install -r requirements.txt

collect:
	$(PYTHON) scripts/collect_datatracker.py
	$(PYTHON) scripts/collect_mailarchive.py
	$(PYTHON) scripts/collect_github.py

normalize:
	$(PYTHON) scripts/normalize.py

score:
	$(PYTHON) scripts/score.py

report-daily:
	$(PYTHON) scripts/report.py --mode daily

report-weekly:
	$(PYTHON) scripts/report.py --mode weekly

prune:
	bash ../../scripts/prune.sh .

update: collect normalize score report-daily prune

weekly: collect normalize score report-weekly prune
