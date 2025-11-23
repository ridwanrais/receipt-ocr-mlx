.PHONY: install run test clean help

help:
	@echo "MLX-VLM Receipt Scanner Service"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make run        - Run the service"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Clean up"

install:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	cp .env.example .env
	@echo "✅ Installation complete!"
	@echo "Edit .env file if needed, then run: make run"

run:
	. venv/bin/activate && python app.py

test:
	. venv/bin/activate && python test_service.py

clean:
	rm -rf venv __pycache__ *.pyc .mlx_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
