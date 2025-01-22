"""
Console interface utilities for the research logger.
Provides consistent console output formatting and user interaction.
"""

from rich.console import Console
from rich.theme import Theme
from rich.prompt import Prompt
from rich.panel import Panel
from typing import Any, Optional

# Define custom theme for consistent styling
custom_theme = Theme({
    'info': 'cyan',
    'warning': 'yellow',
    'error': 'red',
    'success': 'green',
    'highlight': 'bold magenta'
})

class ResearchConsole:
    """Custom console class with research-specific formatting."""
    
    def __init__(self):
        self.console = Console(theme=custom_theme)
        
    def log(self, message: str, style: Optional[str] = None) -> None:
        """Log a message with optional styling."""
        self.console.print(message, style=style)
        
    def error(self, message: str) -> None:
        """Log an error message."""
        self.console.print(f"[error]Error: {message}[/error]")
        
    def success(self, message: str) -> None:
        """Log a success message."""
        self.console.print(f"[success]{message}[/success]")
        
    def warning(self, message: str) -> None:
        """Log a warning message."""
        self.console.print(f"[warning]Warning: {message}[/warning]")
        
    def info(self, message: str) -> None:
        """Log an informational message."""
        self.console.print(f"[info]{message}[/info]")
        
    def display_header(self, text: str) -> None:
        """Display a section header."""
        self.console.print(Panel(text, style="highlight"))
        
    def prompt(self, message: str, default: Any = None) -> str:
        """Get user input with optional default value."""
        return Prompt.ask(message, default=default)
        
    def confirm(self, message: str, default: bool = False) -> bool:
        """Get user confirmation."""
        return Prompt.ask(message, choices=['y', 'n'], default='y' if default else 'n') == 'y'

# Create a global console instance
console = ResearchConsole()