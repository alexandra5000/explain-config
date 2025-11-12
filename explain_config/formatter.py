"""Output formatter for console and markdown."""

from typing import List


class OutputFormatter:
    """Format explanations for console and markdown output."""

    @staticmethod
    def format_for_console(explanations: List[str]) -> str:
        """
        Format explanations for console output.
        
        Args:
            explanations: List of explanation strings (one per component)
            
        Returns:
            Formatted string for console output
        """
        if not explanations:
            return "No components found to explain."
        
        return "\n\n".join(explanations)

    @staticmethod
    def format_for_markdown(explanations: List[str], title: str = "EDOT Configuration Explanation") -> str:
        """
        Format explanations for markdown output.
        
        Args:
            explanations: List of explanation strings (one per component)
            title: Title for the markdown document
            
        Returns:
            Formatted markdown string
        """
        if not explanations:
            return f"# {title}\n\nNo components found to explain."
        
        markdown = f"# {title}\n\n"
        markdown += "This document explains the components found in the EDOT Collector configuration.\n\n"
        markdown += "---\n\n"
        markdown += "\n\n---\n\n".join(explanations)
        
        return markdown

    @staticmethod
    def combine_explanations(explanations: List[str]) -> str:
        """
        Combine multiple explanations into a single formatted string.
        
        Args:
            explanations: List of explanation strings
            
        Returns:
            Combined formatted string
        """
        if not explanations:
            return ""
        
        return "\n\n---\n\n".join(explanations)

