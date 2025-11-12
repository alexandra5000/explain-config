# EDOT Config Explainer

A Python CLI tool that automatically detects and explains all components in Elastic Distribution of OpenTelemetry (EDOT) Collector YAML configurations using local LLMs (Ollama) - **no API keys required!**

## Features

- **Auto-detection**: Automatically identifies receivers, processors, exporters, extensions, and service sections
- **Multiple input methods**: Read from file, stdin, or interactive prompt
- **Formatted output**: Console output with optional markdown export
- **Web UI**: Optional Streamlit interface for easy demos
- **100% Local**: Uses Ollama for local LLM inference - no API keys, completely private

## Installation

**Option 1: Using a virtual environment (recommended)**

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

**Option 2: Install globally (not recommended on macOS)**

```bash
pip3 install -r requirements.txt
```

## Setup

### Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai

### Pull a Model

```bash
# Pull a model (one-time setup)
ollama pull llama3.2        # Small, fast (2GB)
# or
ollama pull llama3.1:8b     # Better quality (4.7GB)
```

### Verify Ollama is Running

```bash
# Start Ollama (usually runs automatically)
ollama serve

# Test it's working
ollama list
```

See [LOCAL_LLM.md](LOCAL_LLM.md) for detailed instructions.

## Usage

**Note:** If using a virtual environment, make sure it's activated:
```bash
source venv/bin/activate
```

### CLI

**From a file:**
```bash
python3 -m explain_config.cli --file config.yaml
```

**From stdin:**
```bash
cat config.yaml | python3 -m explain_config.cli
```

**Interactive prompt:**
```bash
python3 -m explain_config.cli
```

**Export to markdown:**
```bash
python3 -m explain_config.cli --file config.yaml --md-out explanations.md
```

**Use a different model:**
```bash
python3 -m explain_config.cli --file config.yaml --model llama3.1:8b
```

### Web UI

**Simple version:**
```bash
streamlit run app.py
```

**Full-featured version (with file upload, settings):**
```bash
streamlit run streamlit_app.py
```

## Example

Given a YAML config like:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024

exporters:
  elasticsearch:
    endpoints:
      - http://localhost:9200
```

The tool will automatically detect and explain each component with:
- Short title
- Bullet list of field explanations
- "Why it matters" section

## Quick Test

Test with the provided example configs:

```bash
# Test with OTLP receiver
python3 -m explain_config.cli --file test_configs/otlp_receiver.yaml

# Test with batch processor
python3 -m explain_config.cli --file test_configs/batch_processor.yaml

# Test with combined config (multiple components)
python3 -m explain_config.cli --file test_configs/combined.yaml --md-out output.md

# Or run the quick test script
./test_quick.sh
```

See [TESTING.md](TESTING.md) for detailed testing instructions.

## Project Structure

```
explain-config/
├── explain_config/
│   ├── __init__.py
│   ├── cli.py          # Main CLI entry point
│   ├── parser.py       # YAML parsing
│   ├── detector.py     # Component detection
│   ├── explainer.py    # LLM explanation generation
│   └── formatter.py    # Output formatting
├── test_configs/       # Test configuration files
├── streamlit_app.py    # Optional web UI
├── requirements.txt
├── setup.py
└── README.md
```
