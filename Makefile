.PHONY: test

test:
	python -m unittest discover tests
	cd tests/ && go test

run:
	cd service/ && go run host.go
