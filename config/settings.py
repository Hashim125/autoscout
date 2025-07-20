import os
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class AppConfig:
    """Application configuration settings"""
    
    # API Settings
    OPENAI_BASE_URL: str = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL: str = "meta-llama/llama-3-70b-instruct"
    TEMPERATURE: float = 0.7
    
    # UI Settings
    PAGE_TITLE: str = "HashAI"
    PAGE_LAYOUT: str = "wide"
    MAX_DISPLAY_ROWS: int = 10
    
    # Data Settings
    SUPPORTED_FILE_TYPES: List[str] = None
    MAX_FILE_SIZE_MB: int = 50
    
    # Visualization Settings
    REQUIRED_VISUALIZATION_COLUMNS: set = None
    DEFAULT_DPI: int = 150
    
    # Security Settings
    MAX_CODE_EXECUTION_TIME: int = 30  # seconds
    MAX_CODE_LENGTH: int = 5000  # characters
    
    def __post_init__(self):
        if self.SUPPORTED_FILE_TYPES is None:
            self.SUPPORTED_FILE_TYPES = ["csv"]
        if self.REQUIRED_VISUALIZATION_COLUMNS is None:
            self.REQUIRED_VISUALIZATION_COLUMNS = {"x", "y", "end_x", "end_y"}

# Column mapping configuration
COLUMN_ALIASES: Dict[str, str] = {
    # Team variations
    "Squad": "Team",
    "Team Name": "Team", 
    "Squad Name": "Team",
    "Club": "Team",
    "Club Name": "Team",
    "squadName": "Team",
    
    # Player variations
    "Player Name": "Player",
    "Player_Name": "Player",
    "Name": "Player",
    "Full Name": "Player",
    
    # Position variations
    "Position": "Pos",
    "Player Position": "Pos",
    "Role": "Pos",
    
    # Coordinates
    "X": "x",
    "Y": "y", 
    "End X": "end_x",
    "End Y": "end_y",
    "Start X": "start_x",
    "Start Y": "start_y",
    
    # Event types
    "Event": "Event Type",
    "Action": "Event Type",
    "Type": "Event Type",
    
    # Match info
    "Match": "Match ID",
    "Game": "Match ID",
    "Fixture": "Match ID"
}

# Report types configuration
REPORT_TYPES = {
    "Player Report": {
        "description": "Detailed analysis of individual player performance",
        "required_columns": ["Player"],
        "system_prompt": """You are a senior professional football scout preparing reports for coaching and recruitment staff. 
Your writing should be concise, insightful, and focused on decision-making. Evaluate players in terms of:
- Technical ability
- Tactical intelligence  
- Physical performance
- Psychological attributes

Use analytical language but avoid unnecessary jargon. Summarize performance without just listing raw stats."""
    },
    "Match Report": {
        "description": "Comprehensive analysis of match events and performance",
        "required_columns": [],
        "system_prompt": """You are a match analyst writing a post-match report for technical staff. 
Summarize key events, trends, standout performers, and tactical observations using the provided match data. 
Be objective, insightful, and provide interpretation rather than raw numbers."""
    },
    "Opposition Report": {
        "description": "Tactical analysis of opponent team and players",
        "required_columns": ["Team"],
        "system_prompt": """You are a tactical analyst preparing an opposition scouting report for coaches. 
Your focus is on team shape, strengths, weaknesses, key players, transitions, set pieces, and tendencies. 
Use bullet points where appropriate and provide actionable insights backed by data."""
    }
}

# Initialize config
config = AppConfig() 