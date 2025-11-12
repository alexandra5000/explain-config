"""Streamlit web UI for EDOT Config Explainer."""

import streamlit as st
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from explain_config.parser import ConfigParser
from explain_config.detector import ComponentDetector
from explain_config.explainer import OllamaExplainer
from explain_config.formatter import OutputFormatter


def main():
    """Main Streamlit app."""
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
        st.info("💡 Using Ollama - no API key needed!")
        
        model = st.text_input(
            "Model",
            value="llama3.2",
            help="Ollama model name (e.g., llama3.2, llama3.1:8b, mistral)"
        )
        
        ollama_url = st.text_input(
            "Ollama URL",
            value="http://localhost:11434",
            help="Ollama API URL"
        )
    
    # Main content area
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Input")
        yaml_input = st.text_area(
            "YAML Configuration",
            height=400,
            placeholder="""receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch:
    timeout: 1s

exporters:
  elasticsearch:
    endpoints:
      - http://localhost:9200"""
        )
        
        # File upload option
        uploaded_file = st.file_uploader(
            "Or upload a YAML file",
            type=['yaml', 'yml']
        )
        
        if uploaded_file is not None:
            yaml_input = uploaded_file.read().decode('utf-8')
            st.text_area("YAML Configuration", value=yaml_input, height=400, key="uploaded")
    
    with col2:
        st.header("Explanations")
        
        if st.button("Explain Configuration", type="primary"):
            if not yaml_input.strip():
                st.error("Please provide a YAML configuration.")
                return
            
            try:
                # Parse YAML
                with st.spinner("Parsing YAML..."):
                    try:
                        config = ConfigParser.parse_string(yaml_input)
                    except ValueError as e:
                        st.error(f"YAML parsing error: {e}")
                        return
                    except Exception as e:
                        st.error(f"Error parsing YAML: {e}")
                        return
                
                # Validate
                if not ConfigParser.validate_otel_config(config):
                    st.warning("This doesn't look like an OTel/EDOT Collector configuration.")
                
                # Detect components
                components = ComponentDetector.detect_components(config)
                
                if not components:
                    st.info("No components found in the configuration.")
                    return
                
                st.info(f"Found {len(components)} component(s) to explain.")
                
                # Initialize explainer
                try:
                    explainer = OllamaExplainer(model=model, base_url=ollama_url)
                except ValueError as e:
                    st.error(f"Configuration Error: {e}")
                    st.info("Make sure Ollama is running: `ollama serve`")
                    return
                except Exception as e:
                    st.error(f"Error initializing Ollama: {e}")
                    st.info("Make sure Ollama is installed and running. See https://ollama.ai")
                    return
                
                # Generate explanations
                explanations = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, (component_type, component_name, component_config) in enumerate(components):
                    status_text.text(f"Explaining {component_type} '{component_name}' ({i+1}/{len(components)})...")
                    progress_bar.progress((i + 1) / len(components))
                    
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
                        st.warning(f"Failed to explain {component_name}: {e}")
                
                progress_bar.empty()
                status_text.empty()
                
                # Display explanations
                combined = OutputFormatter.combine_explanations(explanations)
                st.markdown(combined)
                
                # Download button for markdown
                markdown_output = OutputFormatter.format_for_markdown(explanations)
                st.download_button(
                    label="📥 Download as Markdown",
                    data=markdown_output,
                    file_name="edot_config_explanation.md",
                    mime="text/markdown"
                )
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.exception(e)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<small>EDOT Config Explainer - Built for Elastic Distribution of OpenTelemetry Collector</small>",
        unsafe_allow_html=True
    )


if __name__ == '__main__':
    main()

