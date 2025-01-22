from pathlib import Path
from core.project_manager import ProjectManager
from core.research_log import ComprehensiveResearchLog
from ui.menus import display_project_selection, display_main_menu
from ui.input_handlers import get_cancellable_input, get_cancellable_multi_input, get_cancellable_number, get_cancellable_parameters
from ui.console import console


def get_application_root() -> Path:
    """
    Determines the application's root directory based on main.py location.
    
    This function creates a reliable way to find the application's base directory
    regardless of where the script is run from. It uses the special __file__ 
    variable which always points to the current script's location.
    
    Returns:
        Path: The absolute path to the application's root directory
    """
    # Get the directory containing main.py
    main_dir = Path(__file__).resolve().parent
    
    # Create a 'research_projects' directory next to main.py
    projects_dir = main_dir / "research_projects"
    
    # Ensure the directory exists
    projects_dir.mkdir(exist_ok=True)
    
    return projects_dir

def main():
    """Main entry point for the research logger application."""
    console.log("[bold blue]Quantitative Research Logger[/bold blue]")
    
    base_dir = get_application_root()
    project_manager = ProjectManager(base_dir)
    
    while True:
        projects = project_manager.find_existing_projects()
        display_project_selection(projects)
        
        console.log("\nOptions:")
        console.log("n/new - Create new project")
        console.log("q/quit - Exit")
        if projects:
            console.log("Or enter a number to open an existing project")
        
        choice = get_cancellable_input("\nEnter your choice")
        if choice is None or choice in ['q', 'quit']:
            console.log("[green]Goodbye![/green]")
            return
            
        if choice in ['n', 'new']:
            result = project_manager.create_new_project()
            if result is None:
                continue
                
            project_name, project_path = result
            research_log = ComprehensiveResearchLog(project_name, project_path)
            console.log(f"[green]Created and opened project: {project_name}[/green]")
        else:
            try:
                selection = int(choice)
                if selection not in projects:
                    console.log("[red]Invalid project number.[/red]")
                    continue
                    
                project = projects[selection]
                research_log = ComprehensiveResearchLog(
                    project['name'],
                    project['path']
                )
                console.log(f"[green]Opened project: {project['name']}[/green]")
            except ValueError:
                console.log("[red]Invalid input. Please enter a number, 'n' for new project, or 'q' to quit.[/red]")
                continue
    
        while True:
            display_main_menu()

            choice = get_cancellable_input("\nEnter your choice (1-10)")
            if choice is None:
                console.log("[green]Exiting research logger[/green]")
                break

            try:
                if choice == "1":
                    goals = get_cancellable_multi_input("Enter daily goals", "goal")
                    if goals is None:
                        console.log("[yellow]Operation cancelled.[/yellow]")
                        continue
                    research_log.start_day(goals)

                elif choice == "2":
                    research_log.review_daily_goals()

                elif choice == "3":
                    title = get_cancellable_input("Enter idea title")
                    if title is None:
                        continue
                    
                    description = get_cancellable_input("Enter description")
                    if description is None:
                        continue
                    
                    research_log.add_idea(title, description)

                elif choice == "4":
                    observation = get_cancellable_input("Enter observation")
                    if observation is None:
                        continue
                    
                    implications = get_cancellable_input("Enter implications")
                    if implications is None:
                        continue
                    
                    research_log.add_insight(observation, implications)

                elif choice == "5":
                    notebook_id = get_cancellable_input("Enter notebook ID")
                    if notebook_id is None:
                        continue
                    
                    page_number = get_cancellable_number("Enter page number")
                    if page_number is None:
                        continue
                    
                    note_type = get_cancellable_input("Enter note type (H/E/R/I/Q)")
                    if note_type is None:
                        continue
                    if note_type not in ['H', 'E', 'R', 'I', 'Q']:
                        console.log("[red]Invalid note type. Must be H, E, R, I, or Q.[/red]")
                        continue
                    
                    summary = get_cancellable_input("Enter summary")
                    if summary is None:
                        continue
                    
                    research_log.add_paper_note(notebook_id, page_number, note_type, summary)

                elif choice == "6":
                    hypothesis = get_cancellable_input("Enter experiment hypothesis")
                    if hypothesis is None:
                        continue
                    
                    methodology = get_cancellable_input("Enter methodology")
                    if methodology is None:
                        continue
                    
                    parameters = get_cancellable_parameters()
                    if parameters is None:
                        continue
                    
                    related_idea = get_cancellable_input("Related idea ID (optional)", allow_empty=True)
                    if related_idea is None:
                        continue

                    research_log.start_experiment(
                        hypothesis=hypothesis,
                        methodology=methodology,
                        parameters=parameters,
                        related_idea_id=related_idea if related_idea else None
                    )

                elif choice == "7":
                    research_log.generate_weekly_digest()

                elif choice == "8":
                    days = get_cancellable_number("Enter days threshold (default 30)", allow_empty=True)
                    if days is None:
                        days = 30
                    research_log.get_stale_ideas(days)

                elif choice == "9":
                    if not research_log.current_experiment:
                        console.log("[red]No active experiment to conclude[/red]")
                        continue
                    
                    conclusions = get_cancellable_input("Enter conclusions")
                    if conclusions is None:
                        continue
                    
                    next_steps = get_cancellable_input("Enter next steps")
                    if next_steps is None:
                        continue
                    
                    research_log.conclude_experiment(conclusions, next_steps)

                elif choice == "10":
                    backup_path = get_cancellable_input("Enter backup path (optional)", allow_empty=True)
                    if backup_path is None:
                        continue

                    backup_dir = Path(backup_path) if backup_path else None
                    research_log.backup_research_data(backup_dir)

                else:
                    console.log("[red]Invalid choice[/red]")

            except Exception as e:
                console.log(f"[red]Error: {str(e)}[/red]")
                console.log("[yellow]Returning to main menu.[/yellow]")


if __name__ == "__main__":
    main()
