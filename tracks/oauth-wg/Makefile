PYTHON ?= python3

.PHONY: install collect normalize score report-daily report-weekly prune update weekly

install:
	$(PYTHON) -m pip install -r requirements.txt

collect:
	bash scripts/collect_all.sh

normalize:
	$(PYTHON) scripts/normalize.py

score:
	$(PYTHON) scripts/score.py

report-daily:
	$(PYTHON) scripts/build_daily_report.py

report-weekly:
	$(PYTHON) scripts/build_weekly_report.py

prune:
	bash ../../scripts/prune.sh .

update: collect normalize score report-daily prune

weekly: collect normalize score report-weekly prune
