"""
Formatting utilities for the research logger.
Provides consistent formatting for dates, times, and other data types.
"""

from datetime import datetime
from typing import Any, Dict
from rich.table import Table
from rich.text import Text

def format_date(dt: datetime) -> str:
    """Format a datetime object for display in logs and UI."""
    return dt.strftime("%Y-%m-%d")

def format_time(dt: datetime) -> str:
    """Format a datetime object with time for detailed logging."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def format_duration(seconds: float) -> str:
    """Format a duration in seconds to a human-readable string."""
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"

def create_idea_table(ideas: Dict[str, Any]) -> Table:
    """Creates a formatted table for displaying ideas."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Status")
    table.add_column("Priority")
    table.add_column("Last Updated")
    
    for idea_id, idea in ideas.items():
        status_color = {
            "seed": "blue",
            "germinating": "green",
            "developing": "yellow",
            "blocked": "red",
            "ready": "bold green"
        }.get(idea.status.value, "white")
        
        table.add_row(
            idea_id,
            idea.title,
            Text(idea.status.value, style=status_color),
            str(idea.priority),
            format_date(idea.last_updated)
        )
    
    return table

def format_experiment_summary(experiment: Dict[str, Any]) -> str:
    """Creates a formatted summary of an experiment."""
    return f"""
Experiment Summary
-----------------
Hypothesis: {experiment['hypothesis']}
Started: {format_time(experiment['timestamp'])}
Status: {'Ongoing' if experiment.get('conclusions') is None else 'Completed'}
Methodology: {experiment['methodology']}
Parameters: {', '.join(f'{k}={v}' for k, v in experiment['parameters'].items())}
"""