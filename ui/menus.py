from rich.table import Table
from core.project_manager import ProjectManager
from ui.input_handlers import get_cancellable_input
from ui.console import console
from typing import Dict

def display_project_selection(projects: Dict[int, Dict]) -> None:
    """Display available projects in a formatted table."""
    if projects:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Selection")
        table.add_column("Project Name")
        table.add_column("Last Modified")
        
        for num, project in projects.items():
            table.add_row(
                str(num),
                project['name'],
                project['last_modified'].strftime("%Y-%m-%d %H:%M")
            )
        
        console.log(table)
    else:
        console.log("[yellow]No existing projects found.[/yellow]")

def display_main_menu() -> None:
    """Display the main action menu."""
    console.log("\n[bold]Available Actions:[/bold]")
    console.log("1. Start Day")
    console.log("2. Review Daily Goals")
    console.log("3. Add Research Idea")
    console.log("4. Add Insight")
    console.log("5. Add Paper Note")
    console.log("6. Start Experiment")
    console.log("7. Generate Weekly Digest")
    console.log("8. Check Stale Ideas")
    console.log("9. Conclude Experiment")
    console.log("10. Create Backup")
