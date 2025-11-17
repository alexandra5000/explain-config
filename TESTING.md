# Testing guide

This guide shows you how to test the EDOT Config Explainer tool.

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install and set up Ollama:**
   ```bash
   # Install Ollama
   brew install ollama  # macOS
   # or visit https://ollama.ai
   
   # Pull a model
   ollama pull llama3.2
   
   # Make sure Ollama is running
   ollama serve
   ```

## Quick test

### Test 1: Single component (OTLP receiver)

```bash
python3 -m explain_config.cli --file test_configs/otlp_receiver.yaml
```

**Expected output:**
- Detects 1 component (OTLP receiver)
- Generates explanation with title, bullet points, and a "Why it matters" section
- Prints formatted explanation to console

### Test 2: Batch processor

```bash
python3 -m explain_config.cli --file test_configs/batch_processor.yaml
```

**Expected output:**
- Detects 1 component (Batch processor)
- Explains `send_batch_max_size` and `timeout` fields

### Test 3: Sending queue

```bash
python3 -m explain_config.cli --file test_configs/sending_queue.yaml
```

**Expected output:**
- Detects 1 component (OTLP exporter)
- Explains sending queue configuration

### Test 4: TLS config

```bash
python3 -m explain_config.cli --file test_configs/tls_config.yaml
```

**Expected output:**
- Detects 1 component (OTLP exporter)
- Explains TLS configuration options

### Test 5: Combined config (multiple components)

```bash
python3 -m explain_config.cli --file test_configs/combined.yaml
```

**Expected output:**
- Detects 3 components (receiver, processor, exporter)
- Generates explanations for each component
- Shows progress for each component

### Test 6: Export to markdown

```bash
python3 -m explain_config.cli --file test_configs/combined.yaml --md-out output.md
```

**Expected output:**
- Generates explanations
- Creates `output.md` file with formatted markdown
- Prints confirmation message

### Test 7: Stdin input

```bash
cat test_configs/otlp_receiver.yaml | python3 -m explain_config.cli
```

**Expected output:**
- Reads from stdin
- Processes and explains the config

### Test 8: Interactive prompt

```bash
python3 -m explain_config.cli
```

Then paste your YAML config and press Ctrl+D (Mac/Linux) or Ctrl+Z (Windows).

## Testing the web UI

1. **Start Streamlit:**

   ```bash
   streamlit run app.py
   ```

2. **Open browser:** 

   Navigate to `http://localhost:8501`.

3. **Test steps:**
   - Paste YAML config in the left text area (or upload a file)
   - Click "Explain Configuration"
   - Watch progress bar as explanations are generated
   - Review explanations in the right panel
   - Download markdown if needed

## Expected behavior

**Valid YAML with components:**
- Parses successfully
- Detects all components
- Generates explanations for each
- Outputs formatted text

**Multiple components:**
- Shows progress for each component
- Explains each component separately
- Combines all explanations in output

**Markdown export:**
- Creates properly formatted markdown file
- Includes title and all explanations

### Error cases

**Invalid YAML:**
```
Error parsing YAML: Invalid YAML: ...
```

**Missing API key:**
```
Error: OpenAI API key not found. Set OPENAI_API_KEY environment variable...
```

**Empty config:**
```
No components found in the configuration.
```

**File not found:**
```
Config file not found: nonexistent.yaml
```

## Verification checklist

- [ ] CLI reads from file correctly
- [ ] CLI reads from stdin correctly
- [ ] CLI handles interactive input
- [ ] Components are auto-detected correctly
- [ ] Explanations are generated in correct format (title, bullets, "Why it matters")
- [ ] Markdown export works
- [ ] Web UI loads and displays correctly
- [ ] Web UI processes configs correctly
- [ ] Error messages are clear and helpful
- [ ] Progress indicators work for multiple components

## Troubleshooting

**No module named 'explain_config'**

Solution: 
- Make sure you're in the project root directory

or

- Install the package: `pip install -e .`

**Cannot connect to Ollama**

Solution: 
- Make sure Ollama is running: `ollama serve`
- Check if it's accessible: `curl http://localhost:11434/api/tags`

**Model not found**

Solution: 
- Pull the model first: `ollama pull llama3.2`
- Check available models: `ollama list`

**Explanations are generic or incorrect**

Solution: 
- The LLM might need better context. Check that your YAML is valid EDOT/OTel config format.

## Sample test commands

```bash
# Quick smoke test
python3 -m explain_config.cli --file test_configs/otlp_receiver.yaml

# Full test with all components
python3 -m explain_config.cli --file test_configs/combined.yaml --md-out test_output.md

# Test stdin
echo "receivers:\n  otlp:\n    protocols:\n      grpc:\n        endpoint: 0.0.0.0:4317" | python3 -m explain_config.cli
```

