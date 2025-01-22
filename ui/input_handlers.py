from typing import Optional, List, Dict, Any
from ui.console import console
from pathlib import Path


def get_cancellable_input(prompt: str, allow_empty: bool = False) -> Optional[str]:
    """Get user input with option to cancel and return to main menu."""
    while True:
        value = input(f"{prompt} (q/quit/cancel to go back): ").strip()
        
        if value.lower() in ['q', 'quit', 'cancel']:
            return None
            
        if not allow_empty and not value:
            console.log("[yellow]Input cannot be empty. Please try again or enter 'q' to cancel.[/yellow]")
            continue
            
        return value

def get_cancellable_multi_input(prompt: str, item_name: str = "item") -> Optional[List[str]]:
    """Get multiple lines of input with option to cancel."""
    console.log(f"\n{prompt} (empty line to finish, q/quit/cancel to go back):")
    items = []
    while True:
        value = input("> ").strip()
        
        if value.lower() in ['q', 'quit', 'cancel']:
            return None
            
        if not value and items:
            return items
            
        if value:
            items.append(value)

def get_cancellable_number(prompt: str, allow_empty: bool = False) -> Optional[int]:
    """Get numerical input with validation and cancel option."""
    while True:
        value = get_cancellable_input(prompt, allow_empty)
        if value is None:
            return None
            
        if allow_empty and not value:
            return None
            
        try:
            return int(value)
        except ValueError:
            console.log("[red]Please enter a valid number.[/red]")

def get_cancellable_parameters() -> Optional[Dict[str, Any]]:
    """Get experiment parameters with option to cancel."""
    parameters = {}
    console.log("\nEnter parameters (empty parameter name to finish, q/quit/cancel to go back):")
    while True:
        param_name = get_cancellable_input("Parameter name", allow_empty=True)
        if param_name is None:
            return None
        if not param_name:
            if parameters:
                return parameters
            console.log("[yellow]At least one parameter is required.[/yellow]")
            continue
            
        param_value = get_cancellable_input(f"Value for {param_name}")
        if param_value is None:
            return None
            
        try:
            float_value = float(param_value)
            parameters[param_name] = float_value
        except ValueError:
            parameters[param_name] = param_value
    
    return parameters