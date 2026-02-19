# KTimer ⏱️

A modern, Windows 11-inspired countdown timer built with Python and PySide6.

> **Note:** This project was **vibe coded**. I wanted a slick, functional UI without the headache of manually learning/dealing with every nuance of Qt's layout engine. It's built for speed, aesthetics, and immediate utility.

## Features
- **Modern UI**: Fluent Design-inspired circular progress and dark mode.
- **Quick Presets**: One-tap starts for 1m, 5m, 15m, 30m, and 1h.
- **Custom Input**: Set any minute duration manually.
- **Responsive**: Fully resizable window with dynamic scaling.

## Setup
This project uses [Poetry](https://python-poetry.org/) for dependency management.

```bash
# Install dependencies
poetry install

# Run the timer
poetry run python app.py