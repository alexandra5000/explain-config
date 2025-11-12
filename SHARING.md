# Sharing the Repository

## Making the Repository Available to Your Team

### Option 1: GitHub (Recommended)

1. **Create a new repository on GitHub:**
   - Go to https://github.com/new
   - Repository name: `explain-config` (or your preferred name)
   - Choose **Public** (anyone can see) or **Private** (only you and invited collaborators)
   - **Don't** initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"

2. **Push your code:**
   ```bash
   # Add the remote (replace YOUR_USERNAME with your GitHub username)
   git remote add origin https://github.com/YOUR_USERNAME/explain-config.git
   
   # Push to GitHub
   git push -u origin main
   ```

3. **Share with teammates:**
   - For **Public repos**: Just share the URL: `https://github.com/YOUR_USERNAME/explain-config`
   - For **Private repos**: 
     - Go to Settings → Collaborators
     - Add your teammates by their GitHub username or email
     - They'll receive an invitation

### Option 2: GitLab

1. **Create a new project on GitLab:**
   - Go to https://gitlab.com/projects/new
   - Project name: `explain-config`
   - Visibility: **Public** or **Private**
   - Click "Create project"

2. **Push your code:**
   ```bash
   git remote add origin https://gitlab.com/YOUR_USERNAME/explain-config.git
   git push -u origin main
   ```

### Option 3: Bitbucket

1. **Create a new repository on Bitbucket:**
   - Go to https://bitbucket.org/repo/create
   - Repository name: `explain-config`
   - Access level: **Public** or **Private**
   - Click "Create repository"

2. **Push your code:**
   ```bash
   git remote add origin https://bitbucket.org/YOUR_USERNAME/explain-config.git
   git push -u origin main
   ```

## What Your Teammates Need to Do

Once the repo is shared, your teammates should:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/explain-config.git
   cd explain-config
   ```

2. **Set up the environment:**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Install Ollama:**
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull a model
   ollama pull llama3.2
   ```

4. **Use the tool:**
   ```bash
   # CLI
   python3 -m explain_config.cli --file config.yaml
   
   # Web UI
   streamlit run app.py
   ```

## Quick Setup Script for Teammates

You can create a `setup.sh` script to automate setup:

```bash
#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "✅ Setup complete! Don't forget to install Ollama: brew install ollama"
```

## Important Notes

- **Never commit sensitive data**: The `.gitignore` already excludes `.env` files and API keys
- **Virtual environment**: The `venv/` folder is excluded from git (each person creates their own)
- **Ollama models**: Each person needs to install Ollama and pull models locally (they're not in git)

