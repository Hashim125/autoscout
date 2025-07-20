import re
import difflib
import logging
import autopep8
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import io
import traceback
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Column name mapping for different data providers
COLUMN_ALIASES = {
    # Team variations
    "Squad": "Team",
    "Team Name": "Team", 
    "Squad Name": "Team",
    "Club": "Team",
    "Club Name": "Team",
    
    # Player variations
    "Player Name": "Player",
    "Player_Name": "Player",
    "Name": "Player",
    "Full Name": "Player",
    "playerName": "Player",
    
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

# Dangerous code patterns to block
DANGEROUS_PATTERNS = [
    r'import\s+os',
    r'import\s+subprocess', 
    r'import\s+sys',
    r'open\(',
    r'eval\(',
    r'exec\(',
    r'__import__',
    r'globals\(',
    r'locals\(',
    r'compile\(',
    r'file\(',
    r'input\(',
    r'raw_input\(',
    r'help\(',
    r'vars\(',
    r'dir\(',
    r'type\(',
    r'getattr\(',
    r'setattr\(',
    r'delattr\(',
    r'hasattr\(',
    r'property\(',
    r'super\(',
    r'staticmethod\(',
    r'classmethod\(',
    r'issubclass\(',
    r'isinstance\(',
    r'callable\(',
    r'hash\(',
    r'id\(',
    r'len\(',
    r'abs\(',
    r'all\(',
    r'any\(',
    r'bin\(',
    r'bool\(',
    r'chr\(',
    r'complex\(',
    r'dict\(',
    r'divmod\(',
    r'enumerate\(',
    r'filter\(',
    r'float\(',
    r'format\(',
    r'frozenset\(',
    r'hex\(',
    r'int\(',
    r'list\(',
    r'map\(',
    r'max\(',
    r'min\(',
    r'next\(',
    r'oct\(',
    r'ord\(',
    r'pow\(',
    r'print\(',
    r'range\(',
    r'repr\(',
    r'reversed\(',
    r'round\(',
    r'set\(',
    r'slice\(',
    r'sorted\(',
    r'str\(',
    r'sum\(',
    r'tuple\(',
    r'zip\(',
]

class VisualizationUtils:
    def __init__(self, df):
        self.df = df
        self.original_columns = set(df.columns)
        self.corrections_log = []
        
    def normalize_columns(self) -> pd.DataFrame:
        """Normalize column names using aliases and return normalized dataframe"""
        df_normalized = self.df.copy()
        
        for alias, canonical in COLUMN_ALIASES.items():
            if alias in df_normalized.columns and canonical not in df_normalized.columns:
                df_normalized[canonical] = df_normalized[alias]
                self.corrections_log.append(f"Column mapping: '{alias}' → '{canonical}'")
                logger.info(f"Column mapping: '{alias}' → '{canonical}'")
        
        return df_normalized
    
    def get_available_columns_info(self) -> str:
        """Get formatted string of available columns with their data types"""
        column_info = []
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            sample_values = self.df[col].dropna().head(3).tolist()
            column_info.append(f"- {col} ({dtype}): {sample_values}")
        
        return "\n".join(column_info)
    
    def check_code_safety(self, code: str) -> Tuple[bool, List[str]]:
        """Check if code contains dangerous patterns"""
        issues = []
        
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(f"Blocked dangerous pattern: {pattern}")
        
        return len(issues) == 0, issues
    
    def auto_fix_plot_code(self, code: str) -> Tuple[str, List[str]]:
        """Fix common GPT code errors and return fixed code with corrections log"""
        corrections = []
        fixed_code = code
        
        # Common replacements
        replacements = {
            "mplsoccer()": "Pitch()",
            "mplsoccer.Pitch()": "Pitch()",
            "from mplsoccer import *": "from mplsoccer import Pitch",
            "plt.show()()": "plt.show()",
            "plt.plt.": "plt.",
            "plt..": "plt.",
            "df.plot()": "df.plot()",  # Keep as is
        }
        
        for wrong, right in replacements.items():
            if wrong in fixed_code:
                fixed_code = fixed_code.replace(wrong, right)
                corrections.append(f"Code fix: '{wrong}' → '{right}'")
        
        # Fix invalid column references using difflib
        column_pattern = r"df\[['\"](.*?)['\"]\]"
        matches = re.findall(column_pattern, fixed_code)
        
        for col in matches:
            if col not in self.df.columns:
                close_match = difflib.get_close_matches(col, self.df.columns, n=1, cutoff=0.6)
                if close_match:
                    fixed_code = re.sub(rf"df\[['\"]{re.escape(col)}['\"]\]", f"df['{close_match[0]}']", fixed_code)
                    corrections.append(f"Column fix: '{col}' → '{close_match[0]}'")
                else:
                    corrections.append(f"Warning: Column '{col}' not found and no close match available")
        
        # Auto-format code using autopep8
        try:
            fixed_code = autopep8.fix_code(fixed_code, options={'aggressive': 1})
            corrections.append("Code auto-formatted with autopep8")
        except Exception as e:
            corrections.append(f"Auto-formatting failed: {str(e)}")
        
        return fixed_code, corrections
    
    def execute_code_safely(self, code: str) -> Tuple[bool, str, Optional[io.BytesIO]]:
        """Safely execute matplotlib code and return success status, message, and image buffer"""
        
        # Check code safety first
        is_safe, safety_issues = self.check_code_safety(code)
        if not is_safe:
            return False, f"Code blocked for security reasons: {'; '.join(safety_issues)}", None
        
        # Fix code
        fixed_code, corrections = self.auto_fix_plot_code(code)
        
        # Log all corrections
        for correction in corrections:
            logger.info(correction)
            self.corrections_log.append(correction)
        
        # Create safe execution environment
        safe_globals = {
            'plt': plt,
            'df': self.df,
            'Pitch': Pitch,
            'np': __import__('numpy'),
            'pd': __import__('pandas')
        }
        
        try:
            # Execute the code
            exec(fixed_code, safe_globals)
            
            # Capture the plot
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            plt.clf()  # Clear the plot
            
            return True, f"Code executed successfully. Corrections made: {len(corrections)}", buffer
            
        except Exception as e:
            error_msg = f"Execution error: {str(e)}\nTraceback: {traceback.format_exc()}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def extract_code_blocks(self, text: str) -> List[str]:
        """Extract Python code blocks from text, only after the '## SUGGESTED VISUALIZATIONS' marker."""
        import re
        marker = '## SUGGESTED VISUALIZATIONS'
        start_idx = text.find(marker)
        if start_idx == -1:
            # Fallback: extract all code blocks (legacy behavior)
            code_blocks = re.findall(r"```python(.*?)```", text, re.DOTALL)
        else:
            code_blocks = re.findall(r"```python(.*?)```", text[start_idx:], re.DOTALL)
        return [block.strip() for block in code_blocks if block.strip()]
    
    def get_corrections_summary(self) -> str:
        """Get a summary of all corrections made"""
        if not self.corrections_log:
            return "No corrections were made."
        
        return "\n".join([f"• {correction}" for correction in self.corrections_log]) 