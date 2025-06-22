# Tech Stack

## Core Dependencies
- **Python 3.x**: Main language
- **Standard library only** for core functionality (subprocess, json, datetime, etc.)
- **Claude CLI**: External dependency accessed via subprocess

## Development Tools
- **pytest** (≥7.0.0): Testing framework
- **pytest-cov** (≥4.0.0): Code coverage
- **pytest-timeout** (≥2.1.0): Test timeout management
- **black** (≥22.0.0): Code formatter
- **flake8** (≥4.0.0): Linting
- **mypy** (≥0.990): Type checking
- **markdown** (≥3.3.0): Documentation

## Key Design Choices
- No external ML/AI libraries - uses Claude CLI directly
- Subprocess-based LLM interaction for simplicity
- JSON for structured communication between nodes
- Markdown for prompts and solution formatting
- File-based workspace organization for outputs