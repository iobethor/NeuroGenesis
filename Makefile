 .PHONY: lint test run
 
 lint:
 	ruff check .
 	mypy src
 
 test:
 	pytest
 
 run:
	uvicorn neurogenesis.api.main:app --host 0.0.0.0 --port 6800
