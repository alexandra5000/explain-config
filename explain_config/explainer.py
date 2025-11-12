"""LLM explanation generator for EDOT Collector configurations using Ollama (local LLM)."""

import os
from abc import ABC, abstractmethod
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BaseExplainer(ABC):
    """Base class for explanation generators."""
    
    def _create_prompt(self, component_type: str, component_name: str, 
                      component_config: str) -> str:
        """Create a structured prompt for the LLM."""
        display_name = self._format_component_name(component_type, component_name)
        
        prompt = f"""You are a technical writer at Elastic.

Given a YAML configuration snippet from the Elastic Distribution of OpenTelemetry (EDOT) Collector, explain clearly what each part of the configuration does.

Guidelines:
- Give accurate, non-hallucinated explanations.
- Keep explanations simple, concise, and technically correct.
- Focus on what the user needs to understand: what this config enables, what each field changes, defaults, and gotchas.
- If something is ambiguous, explicitly say "Not enough context to determine."

Output format:
- Short title (as a markdown heading: ### {display_name})
- Bullet list of explanations (each field/configuration option explained)
- Optional "Why it matters" section (if relevant) formatted as a heading: #### Why it matters

Configuration snippet:
```yaml
{component_config}
```

Provide the explanation now:"""
        
        return prompt
    
    def _format_component_name(self, component_type: str, component_name: str) -> str:
        """Format component name for display."""
        name_parts = component_name.split('_')
        capitalized_name = ' '.join(word.capitalize() for word in name_parts)
        
        name_upper = component_name.upper()
        if name_upper in ['OTLP', 'HTTP', 'GRPC', 'JSON', 'YAML', 'TLS', 'SSL']:
            capitalized_name = name_upper
        
        return f"{capitalized_name} {component_type}"
    
    @abstractmethod
    def explain_component(self, component_type: str, component_name: str, 
                         component_config: str) -> str:
        """Generate an explanation for a component."""
        pass


class OllamaExplainer(BaseExplainer):
    """Generate explanations using Ollama (local LLM - no API key needed)."""
    
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama explainer.
        
        Args:
            model: Ollama model name (default: llama3.2)
            base_url: Ollama API base URL (default: http://localhost:11434)
        """
        try:
            import requests
        except ImportError:
            raise ImportError(
                "requests library required for Ollama. Install with: pip install requests"
            )
        
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.requests = requests
        
        # Test connection
        try:
            response = self.requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                raise Exception(f"Ollama not responding at {self.base_url}")
        except self.requests.exceptions.ConnectionError:
            raise Exception(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running. Install from https://ollama.ai"
            )
    
    def explain_component(self, component_type: str, component_name: str, 
                         component_config: str) -> str:
        prompt = self._create_prompt(component_type, component_name, component_config)
        
        try:
            response = self.requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"You are a technical writer specializing in OpenTelemetry and Elastic Stack documentation. Provide clear, accurate, and concise explanations.\n\n{prompt}",
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 1000
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
            
        except self.requests.exceptions.RequestException as e:
            raise Exception(f"Failed to generate explanation with Ollama: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")


# Default explainer (Ollama)
ExplanationGenerator = OllamaExplainer
