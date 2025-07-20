import pandas as pd
import logging
from typing import Tuple, List, Dict, Optional
from pathlib import Path
import streamlit as st
from config.settings import config, COLUMN_ALIASES, REPORT_TYPES
import os

logger = logging.getLogger(__name__)

class DataValidator:
    """Utility class for data validation and sanitization"""
    
    @staticmethod
    def validate_uploaded_file(uploaded_file) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """
        Validate uploaded file
        
        Returns:
            Tuple of (is_valid, error_message, dataframe)
        """
        if uploaded_file is None:
            return False, "No file uploaded", None
        
        # Check file size
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        if file_size_mb > config.MAX_FILE_SIZE_MB:
            return False, f"File too large. Maximum size is {config.MAX_FILE_SIZE_MB}MB", None
        
        # Check file type
        file_extension = Path(uploaded_file.name).suffix.lower()
        if file_extension not in ['.csv']:
            return False, f"Unsupported file type. Please upload a CSV file.", None
        
        try:
            # Try to read the file
            df = pd.read_csv(uploaded_file)
            
            # Basic validation
            if df.empty:
                return False, "File is empty", None
            
            if len(df.columns) < 2:
                return False, "File must have at least 2 columns", None
            
            return True, "File validated successfully", df
            
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return False, f"Error reading file: {str(e)}", None
    
    @staticmethod
    def validate_dataframe_for_report(df: pd.DataFrame, report_type: str) -> Tuple[bool, List[str]]:
        """
        Validate dataframe has required columns for specific report type
        
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        
        if report_type not in REPORT_TYPES:
            return False, [f"Invalid report type: {report_type}"]
        
        required_columns = REPORT_TYPES[report_type]["required_columns"]
        
        # Check for required columns (after normalization)
        missing_columns = []
        for col in required_columns:
            # Check both original and normalized column names
            found = False
            for original_col in df.columns:
                normalized_col = COLUMN_ALIASES.get(original_col, original_col)
                if normalized_col == col:
                    found = True
                    break
            if not found:
                missing_columns.append(col)
        
        if missing_columns:
            return False, [f"Missing required columns for {report_type}: {', '.join(missing_columns)}"]
        
        # Check for data quality issues
        for col in df.columns:
            # Check for too many null values
            null_percentage = df[col].isnull().sum() / len(df) * 100
            if null_percentage > 50:
                warnings.append(f"Column '{col}' has {null_percentage:.1f}% null values")
            
            # Check for single value columns
            if df[col].nunique() == 1:
                warnings.append(f"Column '{col}' has only one unique value")
        
        return True, warnings
    
    @staticmethod
    def validate_visualization_columns(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate dataframe has columns needed for visualizations
        
        Returns:
            Tuple of (can_visualize, list_of_missing_columns)
        """
        missing_columns = []
        
        for required_col in config.REQUIRED_VISUALIZATION_COLUMNS:
            found = False
            for col in df.columns:
                normalized_col = COLUMN_ALIASES.get(col, col)
                if normalized_col == required_col:
                    found = True
                    break
            if not found:
                missing_columns.append(required_col)
        
        can_visualize = len(missing_columns) == 0
        return can_visualize, missing_columns
    
    @staticmethod
    def sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Sanitize dataframe by removing sensitive data and cleaning values
        
        Returns:
            Sanitized dataframe
        """
        df_clean = df.copy()
        
        # Remove columns that might contain sensitive information
        sensitive_columns = ['password', 'token', 'key', 'secret', 'id', 'email']
        columns_to_remove = []
        
        for col in df_clean.columns:
            col_lower = col.lower()
            if any(sensitive in col_lower for sensitive in sensitive_columns):
                if col_lower not in ['player id', 'team id', 'match id']:  # Keep football-related IDs
                    columns_to_remove.append(col)
        
        if columns_to_remove:
            df_clean = df_clean.drop(columns=columns_to_remove)
            logger.info(f"Removed potentially sensitive columns: {columns_to_remove}")
        
        # Clean string columns
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
        
        return df_clean
    
    @staticmethod
    def get_data_summary(df: pd.DataFrame) -> Dict:
        """
        Get summary statistics for the dataframe
        
        Returns:
            Dictionary with data summary
        """
        summary = {
            "rows": len(df),
            "columns": len(df.columns),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 * 1024),
            "null_percentage": (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
            "column_types": df.dtypes.value_counts().to_dict(),
            "sample_columns": list(df.columns[:5])  # First 5 columns
        }
        
        return summary

class InputValidator:
    """Utility class for input validation"""
    
    @staticmethod
    def validate_api_key() -> Tuple[bool, str]:
        """Validate API key is set"""
        api_key = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return False, "OpenRouter API key not found. Please set OPENROUTER_API_KEY in Streamlit secrets or as an environment variable."
        
        if len(api_key) < 10:
            return False, "API key appears to be invalid (too short)."
        
        return True, "API key validated"
    
    @staticmethod
    def validate_report_type(report_type: str) -> bool:
        """Validate report type is supported"""
        return report_type in REPORT_TYPES
    
    @staticmethod
    def validate_model_selection(model: str) -> bool:
        """Validate model selection"""
        # Add validation logic for model selection
        return True  # Placeholder 