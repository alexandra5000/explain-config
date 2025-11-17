# EDOT Config Explainer

EDOT Config Explainer is a Python CLI tool and web application that automatically detects and explains all components in Elastic Distribution of OpenTelemetry (EDOT) Collector YAML configurations using local LLMs (Ollama).

## Features

- **Auto-detection**: Automatically identifies receivers, processors, exporters, extensions, and service sections
- **Multiple input methods**: Read from file, stdin, or interactive prompt
- **Formatted output**: Console output with optional markdown export
- **Web UI**: Optional Streamlit interface
- **100% Local**: Uses Ollama for local LLM inference

## Installation

### **1. Clone the repository:**

   ```bash
   git clone https://github.com/alexandra5000/explain-config.git
   cd explain-config
   ```

### **2. Set up the virtual environment:**

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

### **3. Install Ollama:**

  Download from https://ollama.ai.

### **4. Pull a model:**

  ```bash
  # Pull a model (one-time setup)
  ollama pull llama3.2        # Default, small, fast (2GB)
  # or
  ollama pull llama3.1:8b     # Better quality (4.7GB)
  ```

### **5. (Optional) Verify Ollama is running:**

  ```bash
  ollama list
  ```

  Refer to [LOCAL_LLM.md](LOCAL_LLM.md) for detailed instructions.

### **6. Use the tool:**

  * **Web UI (recommended)**

    ```bash
    streamlit run app.py
    ```
  
  * **CLI**

    ```bash
    python3 -m explain_config.cli --file your-config.yaml
    ```