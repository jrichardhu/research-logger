from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pathlib import Path

class IdeaStatus(Enum):
    """Status states for research ideas"""
    SEED = "seed"
    GERMINATING = "germinating"
    DEVELOPING = "developing"
    BLOCKED = "blocked"
    READY = "ready"

@dataclass
class PaperNoteReference:
    """Reference to a physical notebook entry"""
    notebook_id: str
    page_number: int
    date: datetime
    note_type: str
    brief_summary: str

@dataclass
class ResearchIdea:
    """Representation of a research idea and its metadata"""
    id: str
    title: str
    description: str
    status: IdeaStatus
    created_date: datetime
    last_updated: datetime
    prerequisites: List[str]
    paper_notes: List[PaperNoteReference]
    related_ideas: List[str]
    potential_impact: str
    effort_estimate: str
    next_steps: str
    priority: int

@dataclass
class Experiment:
    """Record of a research experiment"""
    timestamp: datetime
    hypothesis: str
    methodology: str
    results: Dict[str, Any]
    conclusions: str
    next_steps: str
    code_version: str
    parameters: dict
    metrics: Dict[str, Dict[str, Any]]
    paper_notes: List[PaperNoteReference]
    related_ideas: List[str]