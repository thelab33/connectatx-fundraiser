smoke:
	BASE_URL?=http://localhost:5000
	python ci/smoke/wiring_smoketest.py --base $(BASE_URL)

