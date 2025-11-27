# Makefile for GdeDoctor project

.PHONY: help install install-backend install-bot dev dev-backend dev-bot test lint format clean

help:
	@echo "Available commands:"
	@echo "  make install        - Install all dependencies"
	@echo "  make install-backend - Install backend dependencies"
	@echo "  make install-bot    - Install bot dependencies"
	@echo "  make dev            - Run development environment"
	@echo "  make dev-backend    - Run backend only"
	@echo "  make dev-bot        - Run bot only"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"
	@echo "  make clean          - Clean virtual environments"

install: install-backend install-bot

install-backend:
	@echo "Installing backend dependencies..."
	cd backend && python -m venv .venv
	cd backend && .venv/bin/pip install --upgrade pip
	cd backend && .venv/bin/pip install -r requirements.txt
	@echo "✓ Backend dependencies installed"

install-bot:
	@echo "Installing bot dependencies..."
	cd bot && python -m venv .venv
	cd bot && .venv/bin/pip install --upgrade pip
	cd bot && .venv/bin/pip install -r requirements.txt
	@echo "✓ Bot dependencies installed"

dev-backend:
	@echo "Starting backend..."
	cd backend && .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-bot:
	@echo "Starting bot..."
	cd bot && .venv/bin/python -m app.main

dev:
	@echo "Starting development environment..."
	@echo "Backend will run on http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	@make -j2 dev-backend dev-bot

test:
	@echo "Running tests..."
	cd backend && .venv/bin/pytest tests/ -v --cov=app
	cd bot && .venv/bin/pytest tests/ -v

lint:
	@echo "Running linters..."
	cd backend && .venv/bin/ruff check --fix app/
	cd bot && .venv/bin/ruff check --fix app/

format:
	@echo "Formatting code..."
	cd backend && .venv/bin/ruff format app/
	cd bot && .venv/bin/ruff format app/

clean:
	@echo "Cleaning virtual environments..."
	rm -rf backend/.venv
	rm -rf bot/.venv
	@echo "✓ Cleaned"
