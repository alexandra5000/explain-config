# Using Local LLMs (No API Key Required!)

You can use **Ollama** to run LLMs locally on your machine - no API key needed!

## Quick Start with Ollama

### 1. Install Ollama

**macOS:**
```bash
brew install ollama
# Or download from https://ollama.ai
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai

### 2. Start Ollama and Pull a Model

```bash
# Start Ollama (usually runs automatically)
ollama serve

# Pull a model (in another terminal)
ollama pull llama3.2        # Small, fast (2GB)
# or
ollama pull llama3.1:8b     # Better quality (4.7GB)
# or
ollama pull mistral          # Alternative model
```

### 3. Use with EDOT Config Explainer

```bash
# Activate venv
source venv/bin/activate

# Use Ollama (no API key needed!)
python3 -m explain_config.cli --file test_configs/otlp_receiver.yaml

# Use a different model
python3 -m explain_config.cli --file test_configs/otlp_receiver.yaml --model llama3.1:8b
```

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

## Benefits of Local LLMs

✅ **No API key required** - Works completely offline  
✅ **No usage costs** - Free to run  
✅ **Privacy** - Your configs never leave your machine  
✅ **No rate limits** - Run as many explanations as you want  
✅ **Works offline** - Once models are downloaded  

## Benefits

| Feature | Ollama |
|---------|--------|
| API Key | ❌ No |
| Cost | Free |
| Privacy | ✅ 100% Local |
| Speed | Fast (local) |
| Offline | ✅ Yes |

## Troubleshooting

**"Cannot connect to Ollama"**
- Make sure Ollama is running: `ollama serve`
- Check it's accessible: `curl http://localhost:11434/api/tags`

**"Model not found"**
- Pull the model first: `ollama pull llama3.2`
- Check available models: `ollama list`

**Slow responses**
- Try a smaller model (llama3.2 instead of llama3.1:8b)
- Make sure you have enough RAM (models need 2-8GB depending on size)

## Example Usage

```bash
# Basic usage
python3 -m explain_config.cli --file config.yaml

# With custom model
python3 -m explain_config.cli --model mistral --file config.yaml

# Export to markdown
python3 -m explain_config.cli --file config.yaml --md-out output.md
```

