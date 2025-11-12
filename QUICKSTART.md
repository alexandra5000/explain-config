# Quick Start Guide

## Step 1: Install Ollama

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

## Step 2: Pull a Model

```bash
# Pull a model (one-time setup, ~2GB download)
ollama pull llama3.2

# Or for better quality (larger, ~4.7GB)
ollama pull llama3.1:8b
```

## Step 3: Set Up Python Environment

```bash
# Activate the virtual environment
source venv/bin/activate

# Install dependencies (if not already done)
pip install -r requirements.txt
```

## Step 4: Verify Ollama is Running

```bash
# Check if Ollama is running
ollama list

# If not running, start it
ollama serve
```

## Step 5: Test It!

```bash
# Make sure venv is activated
source venv/bin/activate

# Test with the OTLP receiver example
python3 -m explain_config.cli --file test_configs/otlp_receiver.yaml
```

## Troubleshooting

**"Cannot connect to Ollama" error:**
- Make sure Ollama is running: `ollama serve`
- Check it's accessible: `curl http://localhost:11434/api/tags`
- Verify Ollama is installed: `which ollama`

**"Model not found" error:**
- Pull the model first: `ollama pull llama3.2`
- Check available models: `ollama list`

**"No module named 'explain_config'" error:**
- Make sure you're in the project root directory
- Activate the virtual environment: `source venv/bin/activate`

**Slow responses:**
- Try a smaller model (llama3.2 instead of llama3.1:8b)
- Make sure you have enough RAM (models need 2-8GB depending on size)

## Available Models

Popular models for technical documentation:

- `llama3.2` - Fast, small (2GB), good for quick explanations
- `llama3.1:8b` - Better quality, still fast (4.7GB)
- `mistral` - Alternative, good quality
- `codellama` - Specialized for code/technical content

See all available models:
```bash
ollama list
```

## Next Steps

- See [LOCAL_LLM.md](LOCAL_LLM.md) for more details on using Ollama
- See [TESTING.md](TESTING.md) for comprehensive testing guide
- Try the web UI: `streamlit run streamlit_app.py`
