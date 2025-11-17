"""Simple Streamlit web UI for EDOT Config Explainer."""

import streamlit as st
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from explain_config.parser import ConfigParser
from explain_config.detector import ComponentDetector
from explain_config.explainer import OllamaExplainer
from explain_config.formatter import OutputFormatter
from explain_config.docs_manager import DocsManager


def explain_config(yaml_input: str, model: str = "llama3.2", use_docs: bool = True) -> str:
    """
    Explain a YAML configuration.
    
    Args:
        yaml_input: YAML configuration string
        model: Ollama model name to use
        
    Returns:
        Formatted explanation as markdown string
    """
    # Parse YAML
    config = ConfigParser.parse_string(yaml_input)
    
    # Detect components
    components = ComponentDetector.detect_components(config)
    
    if not components:
        return "No components found in the configuration."
    
    # Initialize explainer
    explainer = OllamaExplainer(model=model, use_docs=use_docs)
    
    # Generate explanations
    explanations = []
    for component_type, component_name, component_config in components:
        try:
            # Format component config for explanation
            component_yaml = ComponentDetector.format_component_for_explanation(
                component_type, component_name, component_config
            )
            
            explanation = explainer.explain_component(
                component_type, component_name, component_yaml
            )
            explanations.append(explanation)
        except Exception as e:
            error_msg = f"### {ComponentDetector.get_component_display_name(component_type, component_name)}\n\n"
            error_msg += f"Error generating explanation: {str(e)}"
            explanations.append(error_msg)
    
    # Format and return
    return OutputFormatter.combine_explanations(explanations)


# Streamlit UI
st.set_page_config(
    page_title="EDOT Config Explainer",
    page_icon="📖",
    layout="wide"
)

st.title("📖 EDOT Config Explainer")
st.markdown("Explain Elastic Distribution of OpenTelemetry Collector configurations")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    model_name = st.text_input(
        "Ollama Model",
        value="llama3.2",
        help="Name of the Ollama model to use (e.g., llama3.2, llama3.1:8b)"
    )
    
    use_docs = st.checkbox(
        "Use Elastic Documentation",
        value=True,
        help="Include up-to-date Elastic documentation context in explanations"
    )
    
    st.divider()
    st.subheader("Documentation")
    
    docs_manager = DocsManager(include_upstream=True)
    cache_status = docs_manager.get_cache_status()
    
    st.write("**Elastic Docs:**")
    if cache_status["cached"]:
        st.success("✓ Cached")
        st.caption(f"Updated: {cache_status['last_updated']}")
        if cache_status["stale"]:
            st.warning("⚠ Stale (>7 days)")
    else:
        st.info("Will download on first use")
    
    if cache_status.get("upstream_enabled"):
        st.write("**OpenTelemetry Docs:**")
        if cache_status.get("otel_cached"):
            st.success("✓ Cached")
            st.caption(f"Updated: {cache_status.get('otel_last_updated', 'Never')} ({cache_status.get('otel_files', 0)} files)")
            if cache_status.get("otel_stale"):
                st.warning("⚠ Stale (>7 days)")
        else:
            st.info("Will download on first use")
    
    if st.button("🔄 Refresh Docs", help="Force download latest documentation"):
        with st.spinner("Downloading latest documentation..."):
            try:
                docs_manager.download_docs(force=True)
                if docs_manager.include_upstream:
                    docs_manager.download_otel_docs(force=True)
                st.success("Documentation refreshed!")
                st.rerun()
            except Exception as e:
                st.error(f"Error refreshing docs: {e}")

yaml_input = st.text_area(
    "Paste your EDOT configuration YAML",
    height=300,
    placeholder="""receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch:
    timeout: 1s"""
)

if st.button("Explain", type="primary"):
    if not yaml_input.strip():
        st.error("Please provide a YAML configuration.")
    else:
        try:
            with st.spinner("Generating explanation..."):
                explanation = explain_config(yaml_input, model=model_name, use_docs=use_docs)
                st.markdown(explanation)
        except Exception as e:
            st.error(f"Error: {str(e)}")
            if "Cannot connect to Ollama" in str(e):
                st.info("💡 Make sure Ollama is running: `ollama serve`")

