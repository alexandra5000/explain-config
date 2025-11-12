"""CLI interface for EDOT Config Explainer."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from explain_config.parser import ConfigParser
from explain_config.detector import ComponentDetector
from explain_config.explainer import OllamaExplainer
from explain_config.formatter import OutputFormatter


def get_input_content(args: argparse.Namespace) -> str:
    """
    Get YAML content from file, stdin, or interactive prompt.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        YAML content as string
    """
    # Priority 1: File
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {args.file}")
        except PermissionError:
            raise PermissionError(f"Permission denied: {args.file}")
        except Exception as e:
            raise Exception(f"Error reading file {args.file}: {str(e)}")
    
    # Priority 2: stdin (check if stdin has data)
    if not sys.stdin.isatty():
        return sys.stdin.read()
    
    # Priority 3: Interactive prompt
    print("Enter your EDOT Collector YAML configuration (press Ctrl+D or Ctrl+Z when done):")
    print("=" * 70)
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    return '\n'.join(lines)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Explain EDOT Collector YAML configuration components",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From file
  python3 -m explain_config.cli --file config.yaml
  
  # From stdin
  cat config.yaml | python3 -m explain_config.cli
  
  # Interactive prompt
  python3 -m explain_config.cli
  
  # Export to markdown
  python3 -m explain_config.cli --file config.yaml --md-out explanations.md
  
  # Use a different model
  python3 -m explain_config.cli --file config.yaml --model llama3.1:8b
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Path to YAML configuration file'
    )
    
    parser.add_argument(
        '--md-out',
        type=str,
        help='Optional: Export explanations to a markdown file'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='llama3.2',
        help='Ollama model name (default: llama3.2)'
    )
    
    parser.add_argument(
        '--ollama-url',
        type=str,
        default='http://localhost:11434',
        help='Ollama API URL (default: http://localhost:11434)'
    )
    
    args = parser.parse_args()
    
    try:
        # Get YAML content
        yaml_content = get_input_content(args)
        
        if not yaml_content.strip():
            print("Error: No YAML content provided.", file=sys.stderr)
            sys.exit(1)
        
        # Parse YAML
        try:
            config = ConfigParser.parse_string(yaml_content)
        except Exception as e:
            print(f"Error parsing YAML: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Validate it's an OTel config
        if not ConfigParser.validate_otel_config(config):
            print("Warning: This doesn't look like an OTel/EDOT Collector configuration.", file=sys.stderr)
            print("Proceeding anyway...", file=sys.stderr)
        
        # Detect components
        components = ComponentDetector.detect_components(config)
        
        if not components:
            print("No components found in the configuration.", file=sys.stderr)
            sys.exit(0)
        
        print(f"Found {len(components)} component(s) to explain...", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        
        # Initialize explanation generator
        try:
            explainer = OllamaExplainer(model=args.model, base_url=args.ollama_url)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error initializing Ollama: {e}", file=sys.stderr)
            print("Make sure Ollama is running: ollama serve", file=sys.stderr)
            sys.exit(1)
        
        # Generate explanations
        explanations = []
        for i, (component_type, component_name, component_config) in enumerate(components, 1):
            print(f"Explaining {component_type} '{component_name}' ({i}/{len(components)})...", 
                  file=sys.stderr)
            
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
                print(f"  Warning: Failed to explain {component_name}: {e}", file=sys.stderr)
        
        # Format and output
        console_output = OutputFormatter.format_for_console(explanations)
        print("\n" + "=" * 70)
        print(console_output)
        
        # Export to markdown if requested
        if args.md_out:
            try:
                markdown_output = OutputFormatter.format_for_markdown(explanations)
                output_path = Path(args.md_out)
                output_path.write_text(markdown_output, encoding='utf-8')
                print(f"\nExplanations exported to: {args.md_out}", file=sys.stderr)
            except PermissionError:
                print(f"Error: Permission denied writing to {args.md_out}", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Error writing markdown file: {e}", file=sys.stderr)
                sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

