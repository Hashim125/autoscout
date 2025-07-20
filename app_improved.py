import streamlit as st
import pandas as pd
import time
import logging
from typing import Optional, Tuple
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Import our services and utilities
from config.settings import config, REPORT_TYPES
from services.openai_service import OpenAIService
from utils.visualization_utils import VisualizationUtils
from utils.prompt_builder import build_prompt
from utils.validators import DataValidator, InputValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
@st.cache_resource
def get_openai_service():
    return OpenAIService()

def main():
    """Main application function"""
    
    # Page configuration
    st.set_page_config(
        page_title=config.PAGE_TITLE,
        layout=config.PAGE_LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">⚽ HashAI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Football Intelligence Report Generator</p>', unsafe_allow_html=True)
    
    # Initialize services
    openai_service = get_openai_service()
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Upload & Settings")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload match or player CSV",
            type=config.SUPPORTED_FILE_TYPES,
            help="Upload a CSV file containing match or player data."
        )
        
        # Report type selection (no descriptions)
        report_type = st.selectbox(
            "Select report type",
            options=list(REPORT_TYPES.keys()),
            help="Choose the type of report you want to generate."
        )
        
        # Advanced settings
        with st.expander("⚙️ Advanced Settings"):
            # Model selection (only Llama 3 70B)
            models = openai_service.get_available_models()
            model_keys = list(models.keys())
            selected_model = model_keys[0]
            st.markdown(f"**AI Model:** {models[selected_model]}")
            
            # Temperature
            temperature = st.slider(
                "Creativity (Temperature)",
                min_value=0.0,
                max_value=1.0,
                value=config.TEMPERATURE,
                step=0.1,
                help="Higher values make output more creative, lower values more focused"
            )
            
            # Visualization toggle
            visuals_enabled = st.checkbox(
                "Generate visualizations",
                value=False,
                help="Enable AI-generated charts and visualizations"
            )
        
        # API key validation
        api_valid, api_message = InputValidator.validate_api_key()
        if not api_valid:
            st.error(api_message)
            st.stop()
        else:
            st.success("✅ API key validated")
    
    # Main content area
    if uploaded_file:
        # Validate and process uploaded file
        is_valid, message, df = DataValidator.validate_uploaded_file(uploaded_file)
        
        if not is_valid:
            st.error(f"❌ {message}")
            st.stop()
        
        # Sanitize data
        df_clean = DataValidator.sanitize_dataframe(df)
        
        # Initialize visualization utilities and normalize columns
        viz_utils = VisualizationUtils(df_clean)
        df_normalized = viz_utils.normalize_columns()
        
        # Display success message and data preview
        st.success("✅ File uploaded and processed successfully")
        
        # Data summary metrics
        data_summary = DataValidator.get_data_summary(df_normalized)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Rows", f"{data_summary['rows']:,}")
        with col2:
            st.metric("Columns", data_summary['columns'])
        with col3:
            st.metric("Memory", f"{data_summary['memory_usage_mb']:.1f} MB")
        with col4:
            st.metric("Null %", f"{data_summary['null_percentage']:.1f}%")
        
        # Show column normalization info if any changes were made
        if viz_utils.corrections_log:
            with st.expander("📊 Column Normalization Applied"):
                for correction in viz_utils.corrections_log:
                    st.write(f"• {correction}")
        
        # Data preview
        with st.expander("📋 Data Preview"):
            st.dataframe(df_normalized.head(config.MAX_DISPLAY_ROWS), use_container_width=True)
        
        # Validate data for selected report type
        is_valid_for_report, warnings = DataValidator.validate_dataframe_for_report(
            df_normalized, report_type
        )
        
        if not is_valid_for_report:
            st.error(f"❌ {warnings[0]}")
            st.stop()
        
        # Data quality warnings in an expander
        if warnings:
            with st.expander("⚠️ Data quality warnings:"):
                for warning in warnings:
                    st.write(f"• {warning}")
        
        # --- File type detection and robust column checking ---
        def detect_file_type(df):
            # Heuristic: if it has 'Strengths', 'Weaknesses', or 'Summary', it's a scout report
            scout_cols = {"Strengths", "Weaknesses", "Summary"}
            event_cols = {"x", "y", "end_x", "end_y", "Event Type"}
            norm_cols = set([c.strip().lower() for c in df.columns])
            if scout_cols & set(df.columns):
                return "scout_report"
            elif event_cols & norm_cols:
                return "event_data"
            else:
                return "unknown"

        file_type = detect_file_type(df_normalized)
        st.session_state['file_type'] = file_type
        st.info(f"Detected file type: {file_type.replace('_', ' ').title()}")

        # If the file is a scout report and the user selects Player Report, check for 'Player Name' or similar
        if report_type == "Player Report" and file_type == "scout_report":
            player_col = None
            for col in df_normalized.columns:
                if col.lower() in ["player", "player name", "name"]:
                    player_col = col
                    break
            if not player_col:
                st.error("This scout report file does not contain a recognizable player name column. Please check your file.")
                st.stop()
            player_names = df_normalized[player_col].dropna().unique()
            selected_player = st.sidebar.selectbox(
                "Select player for report",
                options=player_names,
                help="Choose a specific player to analyze"
            )
            # Robust filtering: strip and lower for both column and selected value
            mask = df_normalized[player_col].astype(str).str.strip().str.lower() == str(selected_player).strip().lower()
            filtered_df = df_normalized[mask]
            if filtered_df.empty:
                st.error(f"No data found for player '{selected_player}'. Please check your file.")
                st.stop()
            subject = selected_player
            data_to_send = filtered_df
        elif report_type == "Player Report" and file_type != "scout_report":
            # Fallback to original logic
            subject, data_to_send = get_subject_and_data(df_normalized, report_type)
        elif report_type == "Opposition Report" and file_type == "scout_report":
            team_col = None
            for col in df_normalized.columns:
                if col.lower() in ["team", "team name", "squad", "club"]:
                    team_col = col
                    break
            if not team_col:
                st.error("This scout report file does not contain a recognizable team column. Please check your file.")
                st.stop()
            team_names = df_normalized[team_col].dropna().unique()
            selected_team = st.sidebar.selectbox(
                "Select opposition team for report",
                options=team_names,
                help="Choose a specific team to analyze"
            )
            subject = selected_team
            data_to_send = df_normalized[df_normalized[team_col] == selected_team]
        else:
            subject, data_to_send = get_subject_and_data(df_normalized, report_type)

        # If file type is unknown, warn and disable report generation
        if file_type == "unknown":
            st.warning("This file does not match expected formats for event or scout report data. Report generation may not work as intended.")

        # --- END file type detection and robust column checking ---
        
        # Visualization validation
        if visuals_enabled:
            can_visualize, missing_viz_cols = DataValidator.validate_visualization_columns(df_normalized)
            if not can_visualize:
                st.warning(f"⚠️ Visualization may fail — missing columns: {', '.join(missing_viz_cols)}")
        
        # Generate report button
        if st.button("🚀 Generate Report", type="primary", use_container_width=True):
            generate_report(
                openai_service, viz_utils, report_type, data_to_send, 
                subject, visuals_enabled, selected_model, temperature
            )

def get_subject_and_data(df: pd.DataFrame, report_type: str) -> Tuple[str, pd.DataFrame]:
    """Get subject and filtered data based on report type (using normalized DataFrame)"""
    
    if report_type == "Player Report" and "Player" in df.columns:
        player_names = df["Player"].dropna().unique()
        selected_player = st.sidebar.selectbox(
            "Select player for report",
            options=player_names,
            help="Choose a specific player to analyze"
        )
        subject = selected_player
        data_to_send = df[df["Player"] == selected_player]
        
    elif report_type == "Opposition Report" and "Team" in df.columns:
        team_names = df["Team"].dropna().unique()
        selected_team = st.sidebar.selectbox(
            "Select opposition team for report",
            options=team_names,
            help="Choose a specific team to analyze"
        )
        subject = selected_team
        data_to_send = df[df["Team"] == selected_team]
        
    else:
        subject = "the match"
        data_to_send = df
    
    return subject, data_to_send

def generate_report(
    openai_service: OpenAIService,
    viz_utils: VisualizationUtils,
    report_type: str,
    data_to_send: pd.DataFrame,
    subject: str,
    visuals_enabled: bool,
    model: str,
    temperature: float
):
    """Generate the report with spinner/progress and only show the cleaned report after generation."""
    
    # Get system prompt from configuration
    system_prompt = REPORT_TYPES[report_type]["system_prompt"]
    
    # Get available columns info for the prompt
    available_columns_info = viz_utils.get_available_columns_info()
    
    # Build user prompt
    user_prompt = build_prompt(
        report_type,
        data_to_send.to_dict(orient='records'),
        visuals_enabled,
        available_columns_info,
        file_type=st.session_state.get('file_type', None) if 'file_type' in st.session_state else None
    )
    
    # Create containers for better layout
    report_container = st.container()
    viz_container = st.container()
    download_container = st.container()
    
    # Show spinner and progress bar while generating
    with report_container:
        st.markdown("### 📜 Generated Report")
        progress_bar = st.progress(0)
        status_text = st.empty()
        full_response = ""
        with st.spinner("Generating report..."):
            try:
                chunk_count = 0
                for chunk in openai_service.generate_report_stream(
                    system_prompt, user_prompt, model, temperature
                ):
                    full_response += chunk
                    chunk_count += 1
                    progress = min(chunk_count / 100, 0.95)
                    progress_bar.progress(progress)
                    status_text.text(f"Generated {len(full_response)} characters...")
                progress_bar.progress(1.0)
                status_text.text("✅ Report generated successfully!")
            except Exception as e:
                st.error(f"❌ Error generating report: {str(e)}")
                logger.error(f"Report generation error: {e}")
                return
    
    # --- Post-process the response to remove code blocks from the written report ---
    marker = '## SUGGESTED VISUALIZATIONS'
    if marker in full_response:
        report_text, viz_section = full_response.split(marker, 1)
    else:
        report_text, viz_section = full_response, ''
    # Remove all code blocks from the written report
    report_text_clean = re.sub(r'```python[\s\S]*?```', '', report_text)
    report_text_clean = re.sub(r'```[\s\S]*?```', '', report_text_clean)
    # Display the cleaned report (only once, after generation)
    with report_container:
        st.markdown(report_text_clean)
        # --- Centered Feedback section ---
        st.markdown("---")
        st.markdown("#### Was this report helpful?")
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
        feedback = st.session_state.get("feedback", None)
        feedback_time = st.session_state.get("feedback_time", None)
        import time as _time
        FEEDBACK_DISPLAY_SECONDS = 2
        if feedback is None:
            with col2:
                if st.button("👍", key="feedback_up"):
                    st.session_state["feedback"] = "up"
                    st.session_state["feedback_time"] = _time.time()
            with col3:
                if st.button("👎", key="feedback_down"):
                    st.session_state["feedback"] = "down"
                    st.session_state["feedback_time"] = _time.time()
        elif feedback == "up":
            st.success("Thank you for your feedback! 😊")
            if feedback_time and _time.time() - feedback_time > FEEDBACK_DISPLAY_SECONDS:
                st.session_state["feedback"] = None
                st.session_state["feedback_time"] = None
        elif feedback == "down":
            feedback_text = st.text_area("What could be improved?", key="feedback_comment")
            if st.button("Submit Feedback", key="submit_feedback"):
                st.session_state["feedback"] = "submitted"
                st.session_state["feedback_time"] = _time.time()
        elif feedback == "submitted":
            st.success("Thank you for your feedback! We'll use it to improve future reports.")
            if feedback_time and _time.time() - feedback_time > FEEDBACK_DISPLAY_SECONDS:
                st.session_state["feedback"] = None
                st.session_state["feedback_time"] = None
    
    # Handle visualizations (now above download options)
    if visuals_enabled:
        with viz_container:
            st.markdown("### 📊 Suggested Visualizations")
            code_blocks = viz_utils.extract_code_blocks(marker + viz_section)
            if not code_blocks:
                st.info("No visualization suggestions found in the response.")
            else:
                for i, code in enumerate(code_blocks):
                    with st.expander(f"🎯 Suggested Visualization {i+1}", expanded=True):
                        st.code(code, language="python")
                        st.info("💡 Copy this code to your own environment for execution.")
                    st.divider()
    
    # Download functionality (now in an expander, below visualizations)
    with download_container:
        with st.expander("💾 Download Options", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📄 Download as TXT",
                    data=report_text_clean,
                    file_name=f"{report_type.replace(' ', '_').lower()}_{subject}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                st.button("📊 Export as PDF", disabled=True, use_container_width=True)

if __name__ == "__main__":
    main() 