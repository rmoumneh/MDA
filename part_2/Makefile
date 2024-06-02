.PHONY: help install clean help
.DEFAULT_GOAL := help

PROJECT_NAME := $(shell basename "$(shell pwd)")

install: clean
	@echo "\n>>> creating local environment and installing dependencies for project \`$(PROJECT_NAME)\`\n"
	python3 -m venv venv
	. venv/bin/activate && pip3 install -r requirements.txt && pip3 install -r requirements_dev.txt && pip install -e .

clean: clean-env clean-cache clean-artifacts
	@echo "\n>>> cleaning environment and artifacts (if present)\n"

clean-env:
	rm -rf venv/ || true

clean-cache:
	rm -rf .mypy_cache/ .pytest_cache/ .tox/ .coverage || true

clean-artifacts:
	rm -rf .mypy_cache .pytest_cache src/scripts.egg-info  */__pycache__/ src/*/__pycache__/ || true

help:
	@cat Makefile
