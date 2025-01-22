"""
Core research logging functionality.
This module implements the main ResearchLog class that handles all research tracking,
experiment management, and idea organization.
"""

from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import subprocess
from rich.table import Table
from rich.text import Text

from core.models import PaperNoteReference, ResearchIdea, Experiment, IdeaStatus
from utils.file_handlers import save_json, load_json, DateTimeEncoder
from utils.formatters import format_date, format_time
from ui.console import console

class ComprehensiveResearchLog:
    """
    Main research logging class that manages all research activities and artifacts.
    Provides methods for tracking experiments, ideas, and paper notes while
    maintaining data persistence and organization.
    """
    
    def __init__(self, project_name: str, base_path: Path):
        self.project_name = project_name
        self.base_path = Path(base_path)
        self.experiments: List[Experiment] = []
        self.insights: List[Dict[str, Any]] = []
        self.current_experiment: Optional[Experiment] = None
        self.paper_notes: List[PaperNoteReference] = []
        self.ideas: Dict[str, ResearchIdea] = {}
        self.daily_summaries: List[Dict[str, Any]] = []
        
        self._initialize_directory_structure()
        self._load_existing_data()

    def _initialize_directory_structure(self) -> None:
        """Creates the necessary directory structure for research artifacts."""
        dirs = ['experiments', 'ideas', 'daily_logs', 'paper_notes', 
                'figures', 'data', 'models', 'backups']
        for dir_name in dirs:
            (self.base_path / dir_name).mkdir(parents=True, exist_ok=True)

    def _load_existing_data(self) -> None:
        """Loads existing research data from disk, handling potential errors."""
        try:
            # Load ideas with proper type conversion
            ideas_data = load_json(self.base_path / 'ideas' / 'idea_summaries.json')
            if ideas_data:
                for idea_dict in ideas_data:
                    idea_dict['status'] = IdeaStatus(idea_dict['status'])
                    idea_dict['created_date'] = datetime.fromisoformat(idea_dict['created_date'])
                    idea_dict['last_updated'] = datetime.fromisoformat(idea_dict['last_updated'])
                    self.ideas[idea_dict['id']] = ResearchIdea(**idea_dict)
            
            # Load paper notes
            notes_data = load_json(self.base_path / 'paper_notes' / 'note_references.json')
            if notes_data:
                self.paper_notes = [PaperNoteReference(**note) for note in notes_data]
            
            # Load experiments
            experiment_data = load_json(self.base_path / 'experiments' / 'experiments.json')
            if experiment_data:
                self.experiments = [Experiment(**exp) for exp in experiment_data]
            
            console.log("[green]Successfully loaded existing research data[/green]")
        except Exception as e:
            console.log(f"[yellow]Warning: Could not load existing data: {str(e)}[/yellow]")

    def _save_research_state(self) -> None:
        """Saves the current state of all research data."""
        try:
            # Save ideas
            save_json(
                [asdict(idea) for idea in self.ideas.values()],
                self.base_path / 'ideas' / 'idea_summaries.json'
            )
            
            # Save paper notes
            save_json(
                [asdict(note) for note in self.paper_notes],
                self.base_path / 'paper_notes' / 'note_references.json'
            )
            
            # Save experiments
            save_json(
                [asdict(exp) for exp in self.experiments],
                self.base_path / 'experiments' / 'experiments.json'
            )
        except Exception as e:
            console.log(f"[red]Error saving research state: {str(e)}[/red]")

    def _save_idea(self, idea: ResearchIdea):
        """Save idea to disk"""
        ideas_file = self.base_path / 'ideas' / 'idea_summaries.json'
        current_ideas = []
        
        if ideas_file.exists():
            with open(ideas_file, 'r') as f:
                current_ideas = json.load(f)
        
        # Update or add the idea
        idea_dict = asdict(idea)
        idea_dict['status'] = idea.status.value
        idea_dict['created_date'] = idea.created_date.isoformat()
        idea_dict['last_updated'] = idea.last_updated.isoformat()
        
        # Replace or append
        found = False
        for i, existing_idea in enumerate(current_ideas):
            if existing_idea['id'] == idea.id:
                current_ideas[i] = idea_dict
                found = True
                break
        if not found:
            current_ideas.append(idea_dict)
        
        with open(ideas_file, 'w') as f:
            json.dump(current_ideas, f, indent=2, cls=DateTimeEncoder)

    def _get_git_version(self) -> str:
        """Get current git commit hash"""
        try:
            return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
        except:
            return "Git version unavailable"

    def _load_daily_goals(self) -> Dict[str, Any]:
        """Load today's goals and progress from the daily logs."""
        today = datetime.now().strftime("%Y%m%d")
        daily_log_path = self.base_path / 'daily_logs' / f"daily_{today}.json"
        
        if daily_log_path.exists():
            return load_json(daily_log_path)
        return {
            'date': datetime.now().isoformat(),
            'goals': [],
            'completed_tasks': [],
            'insights': [],
            'next_day_todos': [],
            'goal_status': {}  # Tracks status of each goal
        }

    def _get_past_incomplete_goals(self) -> List[Dict[str, Any]]:
        """
        Retrieves incomplete goals from past daily logs.
        Returns a list of dictionaries containing goal details and their original dates.
        """
        incomplete_goals = []
        daily_logs_path = self.base_path / 'daily_logs'
        today = datetime.now().date()
        
        # Iterate through daily log files
        for log_file in daily_logs_path.glob('daily_*.json'):
            # Extract date from filename (daily_YYYYMMDD.json)
            try:
                file_date = datetime.strptime(log_file.stem[6:], '%Y%m%d').date()
                if file_date >= today:
                    continue
                    
                daily_summary = load_json(log_file)
                goals = daily_summary.get('goals', [])
                goal_status = daily_summary.get('goal_status', {})
                
                # Check each goal's status
                for i, goal in enumerate(goals, 1):
                    status = goal_status.get(str(i), {}).get('status', 'pending')
                    if status != 'completed':
                        incomplete_goals.append({
                            'goal': goal,
                            'original_date': file_date.isoformat(),
                            'status': status,
                            'progress_notes': goal_status.get(str(i), {}).get('progress_notes', [])
                        })
            except (ValueError, json.JSONDecodeError) as e:
                console.log(f"[yellow]Warning: Error processing {log_file}: {str(e)}[/yellow]")
        
        return incomplete_goals

    def review_daily_goals(self) -> None:
        """Review and update the status of today's goals, including incomplete goals from past days."""
        daily_summary = self._load_daily_goals()
        goals = daily_summary.get('goals', [])
        goal_status = daily_summary.get('goal_status', {})
        
        # Get incomplete goals from past days
        past_incomplete = self._get_past_incomplete_goals()
        
        if past_incomplete:
            console.display_header("Past Incomplete Goals")
            for i, incomplete in enumerate(past_incomplete):
                console.info(f"Goal from {incomplete['original_date']}: {incomplete['goal']}")
                if console.confirm("Add this goal to today's goals?"):
                    # Add the goal to today's list
                    goals.append(incomplete['goal'])
                    new_goal_index = len(goals)
                    
                    # Transfer the previous status and progress notes
                    goal_status[str(new_goal_index)] = {
                        'status': incomplete['status'],
                        'progress_notes': incomplete['progress_notes'] + [{
                            'time': datetime.now().isoformat(),
                            'note': f"Carried over from {incomplete['original_date']}"
                        }],
                        'completion_time': None
                    }
        
        if not goals:
            console.warning("No goals set for today. Would you like to set some goals now?")
            if console.confirm("Set goals now?"):
                self.start_day([])
                return
            return

        console.display_header("Daily Goals Review")
        
        # Review all goals (both new and carried over)
        for i, goal in enumerate(goals, 1):
            current_status = goal_status.get(str(i), {
                'status': 'pending',
                'progress_notes': [],
                'completion_time': None
            })
            
            console.info(f"\nGoal {i}: {goal}")
            
            # Display if this is a carried-over goal
            for note in current_status['progress_notes']:
                if 'Carried over from' in note['note']:
                    console.info(f"[yellow]This goal was carried over from {note['note'].split('from ')[-1]}[/yellow]")
                    break
            
            console.info(f"Current Status: {current_status['status']}")
            
            if current_status['progress_notes']:
                console.info("Progress Notes:")
                for note in current_status['progress_notes']:
                    if 'Carried over from' not in note['note']:
                        console.log(f"- {note['time']}: {note['note']}")
            
            update = console.confirm("Update this goal?")
            if update:
                new_status = console.prompt(
                    "Status (pending/in_progress/completed/blocked)",
                    default=current_status['status']
                )
                
                if new_status != current_status['status']:
                    current_status['status'] = new_status
                    if new_status == 'completed':
                        current_status['completion_time'] = datetime.now().isoformat()
                
                add_note = console.confirm("Add a progress note?")
                if add_note:
                    note = console.prompt("Enter progress note")
                    current_status['progress_notes'].append({
                        'time': datetime.now().isoformat(),
                        'note': note
                    })
                
                goal_status[str(i)] = current_status
        
        # Update daily summary with modified goals and status
        daily_summary['goals'] = goals
        daily_summary['goal_status'] = goal_status
        save_json(
            daily_summary, 
            self.base_path / 'daily_logs' / f"daily_{datetime.now():%Y%m%d}.json"
        )
        
        self._display_goals_summary(daily_summary)

    def _display_goals_summary(self, daily_summary: Dict[str, Any]) -> None:
        """Display a summary of goals and their progress."""
        goals = daily_summary.get('goals', [])
        goal_status = daily_summary.get('goal_status', {})
        
        console.display_header("Goals Summary")
        
        # Create a progress table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Goal")
        table.add_column("Status")
        table.add_column("Progress")
        table.add_column("Latest Update")
        
        for i, goal in enumerate(goals, 1):
            status = goal_status.get(str(i), {'status': 'pending', 'progress_notes': []})
            
            # Calculate progress indicators
            progress_notes = status['progress_notes']
            latest_note = progress_notes[-1]['note'] if progress_notes else "No updates"
            latest_time = format_time(datetime.fromisoformat(progress_notes[-1]['time'])) if progress_notes else "-"
            
            # Add row with appropriate styling
            status_style = {
                'pending': 'yellow',
                'in_progress': 'blue',
                'completed': 'green',
                'blocked': 'red'
            }.get(status['status'], 'white')
            
            table.add_row(
                goal,
                Text(status['status'], style=status_style),
                latest_note,
                latest_time
            )
        
        console.log(table)
        
        # Show completion statistics
        completed = sum(1 for s in goal_status.values() if s['status'] == 'completed')
        total = len(goals)
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        console.info(f"\nProgress: {completed}/{total} goals completed ({completion_rate:.1f}%)")

    def start_day(self, goals: List[str]) -> dict:
        """
        Begin a new research day with specific goals, preserving existing data if present.
        
        This method checks for an existing daily summary and merges new goals with any
        existing data to maintain continuity throughout the day.
        """
        today = datetime.now()
        daily_log_path = self.base_path / 'daily_logs' / f"daily_{today:%Y%m%d}.json"
        
        # If a daily summary exists, load it first
        if daily_log_path.exists():
            existing_summary = load_json(daily_log_path)
            
            # Preserve existing data while adding new goals
            summary = {
                'date': existing_summary.get('date', today.isoformat()),
                'goals': list(set(existing_summary.get('goals', []) + goals)),
                'completed_tasks': existing_summary.get('completed_tasks', []),
                'insights': existing_summary.get('insights', []),
                'next_day_todos': existing_summary.get('next_day_todos', []),
                'goal_status': existing_summary.get('goal_status', {})
            }
            
            # Initialize status for new goals
            current_goal_count = len(existing_summary.get('goals', []))
            for i, goal in enumerate(goals, current_goal_count + 1):
                if str(i) not in summary['goal_status']:
                    summary['goal_status'][str(i)] = {
                        'status': 'pending',
                        'progress_notes': [{
                            'time': datetime.now().isoformat(),
                            'note': 'Goal added during day'
                        }],
                        'completion_time': None
                    }
        else:
            # Create new summary if no existing file
            summary = {
                'date': today.isoformat(),
                'goals': goals,
                'completed_tasks': [],
                'insights': [],
                'next_day_todos': [],
                'goal_status': {
                    str(i): {
                        'status': 'pending',
                        'progress_notes': [],
                        'completion_time': None
                    }
                    for i, _ in enumerate(goals, 1)
                }
            }
        
        # Update in-memory state
        self.daily_summaries.append(summary)
        
        # Display current goals with their status
        console.display_header("Daily Research Goals")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Goal")
        table.add_column("Status")
        table.add_column("Added")
        
        for i, goal in enumerate(summary['goals'], 1):
            status = summary['goal_status'].get(str(i), {})
            
            # Determine when the goal was added
            notes = status.get('progress_notes', [])
            added_time = "Initial setup"
            if notes and 'Goal added during day' in notes[0]['note']:
                added_time = "Added later"
                
            status_text = status.get('status', 'pending')
            status_style = {
                'pending': 'yellow',
                'in_progress': 'blue',
                'completed': 'green',
                'blocked': 'red'
            }.get(status_text, 'white')
            
            table.add_row(
                goal,
                Text(status_text, style=status_style),
                added_time
            )
        
        console.log(table)
        
        # Save the updated summary
        self._save_daily_summary(summary)
        return summary

    def add_paper_note(self, notebook_id: str, page_number: int, 
                      note_type: str, summary: str) -> PaperNoteReference:
        """Record a new paper note reference"""
        note = PaperNoteReference(
            notebook_id=notebook_id,
            page_number=page_number,
            date=datetime.now(),
            note_type=note_type,
            brief_summary=summary
        )
        self.paper_notes.append(note)
        
        # Save to disk
        notes_file = self.base_path / 'paper_notes' / 'note_references.json'
        current_notes = []
        if notes_file.exists():
            with open(notes_file, 'r') as f:
                current_notes = json.load(f)
        
        current_notes.append(asdict(note))
        with open(notes_file, 'w') as f:
            json.dump(current_notes, f, indent=2, cls=DateTimeEncoder)
        
        console.log(f"[green]Added paper note reference: {summary}[/green]")
        return note

    def add_idea(self, title: str, description: str, 
                 paper_note: Optional[PaperNoteReference] = None) -> str:
        """Capture a new research idea"""
        idea_id = f"IDEA-{datetime.now():%Y%m%d-%H%M}"
        idea = ResearchIdea(
            id=idea_id,
            title=title,
            description=description,
            status=IdeaStatus.SEED,
            created_date=datetime.now(),
            last_updated=datetime.now(),
            prerequisites=[],
            paper_notes=[paper_note] if paper_note else [],
            related_ideas=[],
            potential_impact="",
            effort_estimate="",
            next_steps="Initial exploration needed",
            priority=3
        )
        self.ideas[idea_id] = idea
        self._save_idea(idea)
        
        console.log(f"[green]Added new idea: {title} ({idea_id})[/green]")
        return idea_id

    def get_stale_ideas(self, days_threshold: int = 10) -> List[ResearchIdea]:
        """Find ideas that haven't been updated recently"""
        current_time = datetime.now()
        stale_ideas = [
            idea for idea in self.ideas.values()
            if (current_time - idea.last_updated).days > days_threshold
            and idea.status != IdeaStatus.BLOCKED
        ]
        
        if stale_ideas:
            console.log("\n[yellow]Stale Ideas Found:[/yellow]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("ID")
            table.add_column("Title")
            table.add_column("Status")
            table.add_column("Last Updated")
            
            for idea in stale_ideas:
                table.add_row(
                    idea.id,
                    idea.title,
                    idea.status.value,
                    idea.last_updated.strftime("%Y-%m-%d")
                )
            
            console.log(table)

        else:
            console.log(f"\n[yellow]No Stale Ideas Found > {days_threshold} Days[/yellow]")
        
        return stale_ideas

    def add_insight(self, observation: str, implications: str):
        """Record important insights or realizations"""
        insight = {
            'timestamp': datetime.now(),
            'observation': observation,
            'implications': implications,
            'experiment_id': id(self.current_experiment) if self.current_experiment else None
        }
        self.insights.append(insight)
        
        # Update current experiment if one is active
        if self.current_experiment:
            if 'insights' not in self.current_experiment.results:
                self.current_experiment.results['insights'] = []
            self.current_experiment.results['insights'].append(insight)
        
        # Add to daily summary if one exists
        if self.daily_summaries:
            self.daily_summaries[-1]['insights'].append(insight)
        
        console.log(f"[green]Recorded new insight: {observation}[/green]")
        return insight

    def start_experiment(self, hypothesis: str, methodology: str, 
                        parameters: dict, related_idea_id: Optional[str] = None):
        """Begin a new research experiment"""
        if self.current_experiment:
            console.log("[yellow]Warning: Concluding previous experiment automatically[/yellow]")
            self.conclude_experiment("Automatically concluded", "Switched to new experiment")

        experiment = Experiment(
            timestamp=datetime.now(),
            hypothesis=hypothesis,
            methodology=methodology,
            results={},
            conclusions="",
            next_steps="",
            code_version=self._get_git_version(),
            parameters=parameters,
            metrics={},
            paper_notes=[],
            related_ideas=[related_idea_id] if related_idea_id else []
        )
        
        self.current_experiment = experiment
        
        # Create experiment directory
        exp_dir = self.base_path / 'experiments' / f"experiment_{experiment.timestamp:%Y%m%d_%H%M%S}"
        exp_dir.mkdir(parents=True, exist_ok=True)
        
        # Save initial experiment metadata
        with open(exp_dir / 'metadata.json', 'w') as f:
            json.dump({
                'hypothesis': hypothesis,
                'methodology': methodology,
                'parameters': parameters,
                'related_ideas': experiment.related_ideas,
                'start_time': experiment.timestamp.isoformat()
            }, f, indent=2, cls=DateTimeEncoder)
        
        console.log(f"[green]Started new experiment: {hypothesis}[/green]")
        return experiment

    def conclude_experiment(self, conclusions: str, next_steps: str):
        """Conclude current experiment with findings and future directions"""
        if not self.current_experiment:
            raise ValueError("No active experiment to conclude")
        
        self.current_experiment.conclusions = conclusions
        self.current_experiment.next_steps = next_steps
        
        # Save final results
        exp_dir = self.base_path / 'experiments' / f"experiment_{self.current_experiment.timestamp:%Y%m%d_%H%M%S}"
        
        # Save complete experiment data
        with open(exp_dir / 'results.json', 'w') as f:
            json.dump({
                'hypothesis': self.current_experiment.hypothesis,
                'methodology': self.current_experiment.methodology,
                'parameters': self.current_experiment.parameters,
                'results': self.current_experiment.results,
                'metrics': self.current_experiment.metrics,
                'conclusions': conclusions,
                'next_steps': next_steps,
                'end_time': datetime.now().isoformat()
            }, f, indent=2, cls=DateTimeEncoder)
        
        self.experiments.append(self.current_experiment)
        self.current_experiment = None
        
        console.log("[green]Experiment concluded successfully[/green]")

    def _save_daily_summary(self, summary: Dict[str, Any]) -> None:
        """
        Save or update the daily summary file, preserving file consistency.
        
        This method ensures atomic writes to prevent data corruption and maintains
        proper JSON formatting with datetime handling.
        """
        today = datetime.now()
        daily_log_path = self.base_path / 'daily_logs' / f"daily_{today:%Y%m%d}.json"
        
        try:
            # Create a temporary file for atomic write
            temp_path = daily_log_path.with_suffix('.tmp')
            
            # Prepare the summary for serialization
            serializable_summary = {
                'date': summary['date'] if isinstance(summary['date'], str) 
                       else summary['date'].isoformat(),
                'goals': summary['goals'],
                'completed_tasks': summary['completed_tasks'],
                'insights': summary['insights'],
                'next_day_todos': summary['next_day_todos'],
                'goal_status': summary['goal_status']
            }
            
            # Write to temporary file first
            with open(temp_path, 'w') as f:
                json.dump(serializable_summary, f, indent=2, cls=DateTimeEncoder)
            
            # Atomic rename to ensure file consistency
            temp_path.replace(daily_log_path)
            
            console.log(f"[green]Successfully saved daily summary to {daily_log_path}[/green]")
        except Exception as e:
            console.log(f"[red]Error saving daily summary: {str(e)}[/red]")
            if temp_path.exists():
                temp_path.unlink()
            raise

    def generate_weekly_digest(self) -> str:
        """Create a comprehensive weekly research summary"""
        week_start = datetime.now() - timedelta(days=7)
        
        # Create tables for rich display
        experiments_table = Table(show_header=True, header_style="bold magenta")
        experiments_table.add_column("Hypothesis")
        experiments_table.add_column("Status")
        experiments_table.add_column("Conclusions")
        
        ideas_table = Table(show_header=True, header_style="bold magenta")
        ideas_table.add_column("Priority")
        ideas_table.add_column("Title")
        ideas_table.add_column("Status")
        ideas_table.add_column("Next Steps")
        
        # Active experiments
        recent_experiments = [e for e in self.experiments if e.timestamp > week_start]
        for exp in recent_experiments:
            experiments_table.add_row(
                exp.hypothesis,
                'Ongoing' if exp == self.current_experiment else 'Completed',
                exp.conclusions if exp.conclusions else 'No conclusions yet'
            )
        
        # Ideas progress
        active_ideas = [i for i in self.ideas.values() if i.last_updated > week_start]
        for idea in active_ideas:
            ideas_table.add_row(
                str(idea.priority),
                idea.title,
                idea.status.value,
                idea.next_steps
            )
        
        console.log("\n[bold blue]Weekly Research Digest[/bold blue]")
        console.log("\n[bold]Active Experiments[/bold]")
        console.log(experiments_table)
        console.log("\n[bold]Ideas Progress[/bold]")
        console.log(ideas_table)
        
        return "Weekly digest generated"

    def backup_research_data(self, backup_dir: Optional[Path] = None) -> Path:
        """Create a backup of all research data
        
        Args:
            backup_dir (Optional[Path]): Custom backup directory path.
                If None, creates backup in default location.
        
        Returns:
            Path: Path to the created backup directory
        """
        if backup_dir is None:
            backup_dir = self.base_path / 'backups' / f"backup_{datetime.now():%Y%m%d_%H%M%S}"
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup ideas
        with open(backup_dir / 'ideas.json', 'w') as f:
            json.dump([asdict(idea) for idea in self.ideas.values()], f, indent=2, cls=DateTimeEncoder)
        
        # Backup paper notes
        with open(backup_dir / 'paper_notes.json', 'w') as f:
            json.dump([asdict(note) for note in self.paper_notes], f, indent=2, cls=DateTimeEncoder)
        
        # Backup daily summaries
        with open(backup_dir / 'daily_summaries.json', 'w') as f:
            json.dump(self.daily_summaries, f, indent=2, default=str)
        
        # Backup experiments
        with open(backup_dir / 'experiments.json', 'w') as f:
            json.dump([asdict(exp) for exp in self.experiments], f, indent=2, cls=DateTimeEncoder)
        
        console.log(f"[green]Created backup at {backup_dir}[/green]")
        return backup_dir
