"""Component detector for EDOT Collector configurations."""

from typing import Dict, Any, List, Tuple


class ComponentDetector:
    """Detect and extract components from EDOT Collector configurations."""

    COMPONENT_SECTIONS = {
        'receivers': 'receiver',
        'processors': 'processor',
        'exporters': 'exporter',
        'extensions': 'extension',
    }

    @staticmethod
    def detect_components(config: Dict[str, Any]) -> List[Tuple[str, str, Dict[str, Any]]]:
        """
        Detect all components in the configuration.
        
        Args:
            config: Parsed YAML configuration dictionary
            
        Returns:
            List of tuples: (section_type, component_name, component_config)
            Example: [('receiver', 'otlp', {...}), ('processor', 'batch', {...})]
        """
        components = []
        
        # Detect receivers, processors, exporters, extensions
        for section_key, component_type in ComponentDetector.COMPONENT_SECTIONS.items():
            if section_key in config and isinstance(config[section_key], dict):
                for component_name, component_config in config[section_key].items():
                    # Handle both dict configs and null/empty configs
                    if component_config is None:
                        component_config = {}
                    if isinstance(component_config, dict):
                        components.append((component_type, component_name, component_config))
        
        # Detect service section (special handling)
        if 'service' in config and isinstance(config['service'], dict):
            service_config = config['service']
            components.append(('service', 'service', service_config))
        
        return components

    @staticmethod
    def get_component_display_name(component_type: str, component_name: str) -> str:
        """
        Generate a display name for a component.
        
        Args:
            component_type: Type of component (receiver, processor, exporter, extension, service)
            component_name: Name of the component
            
        Returns:
            Formatted display name (e.g., "OTLP receiver", "Batch processor")
        """
        # Capitalize first letter of component name
        name_parts = component_name.split('_')
        capitalized_name = ' '.join(word.capitalize() for word in name_parts)
        
        # Special handling for common abbreviations
        name_upper = component_name.upper()
        if name_upper in ['OTLP', 'HTTP', 'GRPC', 'JSON', 'YAML']:
            capitalized_name = name_upper
        
        return f"{capitalized_name} {component_type}"

    @staticmethod
    def format_component_for_explanation(component_type: str, component_name: str, 
                                        component_config: Dict[str, Any]) -> str:
        """
        Format a component configuration for LLM explanation.
        
        Args:
            component_type: Type of component
            component_name: Name of the component
            component_config: Component configuration dictionary
            
        Returns:
            Formatted YAML string for the component
        """
        import yaml
        
        # Create a minimal config snippet with just this component
        snippet = {
            component_type + 's': {
                component_name: component_config
            }
        }
        
        return yaml.dump(snippet, default_flow_style=False, sort_keys=False)

