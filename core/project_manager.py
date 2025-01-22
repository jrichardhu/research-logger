from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Optional, Tuple
from ui.console import console
from rich.table import Table

from ui.input_handlers import get_cancellable_input

class ProjectManager:
    """Manages research project discovery, creation, and selection"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(exist_ok=True)
    
    def find_existing_projects(self) -> Dict[int, Dict]:
        """Discover existing research projects in the base directory."""
        projects = {}
        selection_number = 1
        
        if not self.base_dir.exists():
            return projects
            
        for path in self.base_dir.iterdir():
            if not path.is_dir():
                continue
                
            required_dirs = ['experiments', 'ideas', 'daily_logs', 'paper_notes']
            if all((path / subdir).exists() for subdir in required_dirs):
                try:
                    with open(path / 'project_metadata.json', 'r') as f:
                        metadata = json.load(f)
                        project_name = metadata.get('project_name', path.name)
                except:
                    project_name = path.name
                    
                projects[selection_number] = {
                    'path': path,
                    'name': project_name,
                    'last_modified': datetime.fromtimestamp(path.stat().st_mtime)
                }
                selection_number += 1
                
        return projects
    
    def create_new_project(self) -> Optional[Tuple[str, Path]]:
        """Guide the user through creating a new research project."""
        console.log("\n[bold blue]Create New Research Project[/bold blue]")
        
        project_name = get_cancellable_input("Enter project name")
        if project_name is None:
            return None
            
        safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_').lower()
        
        project_path = self.base_dir / safe_name
        
        if project_path.exists():
            console.log("[red]Error: A project with this name already exists.[/red]")
            return None
            
        try:
            project_path.mkdir(parents=True)
            with open(project_path / 'project_metadata.json', 'w') as f:
                json.dump({
                    'project_name': project_name,
                    'created_date': datetime.now().isoformat(),
                    'last_modified': datetime.now().isoformat()
                }, f, indent=2)
            return project_name, project_path
        except Exception as e:
            console.log(f"[red]Error creating project: {str(e)}[/red]")
            return None