init:
	pip install -r requirements.txt

test:
	nosetests tests

run_server:
	python ./server/run.py
