import streamlit as st
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv
from utils.prompt_builder import build_prompt
from utils.visualization_utils import VisualizationUtils
import time

load_dotenv()

st.set_page_config(page_title="HashAI", layout="wide")

st.title("⚽ HashAI – Football Intelligence Report Generator")
st.markdown("""
Welcome to **HashAI**! Upload your match or player CSV data and generate professional scouting, match, or opposition reports powered by AI.\
Select your report type and focus for tailored insights.
""")

with st.sidebar:
    st.header("Upload & Settings")
    uploaded_file = st.file_uploader("Upload match or player CSV", type="csv", help="Upload a CSV file containing match or player data.")
    user_task = st.selectbox(
        "Select report type",
        ["Player Report", "Match Report", "Opposition Report"],
        help="Choose the type of report you want to generate."
    )
    visuals_enabled = st.checkbox("Generate visualizations (matplotlib/mplsoccer)", value=False, help="Enable AI-generated charts and visualizations")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Initialize visualization utilities and normalize columns
    viz_utils = VisualizationUtils(df)
    df_normalized = viz_utils.normalize_columns()
    
    st.success("✅ File uploaded successfully")
    st.dataframe(df_normalized.head(10), use_container_width=True)
    
    # Show column normalization info if any changes were made
    if viz_utils.corrections_log:
        with st.expander("📊 Column Normalization Applied"):
            st.write("The following column mappings were applied:")
            for correction in viz_utils.corrections_log:
                st.write(f"• {correction}")

    subject = None
    data_to_send = df_normalized
    
    # Player or team selection logic using normalized columns
    if user_task == "Player Report" and "Player" in df_normalized.columns:
        player_names = df_normalized["Player"].dropna().unique()
        selected_player = st.sidebar.selectbox("Select player for report", player_names)
        subject = selected_player
        data_to_send = df_normalized[df_normalized["Player"] == selected_player]
    elif user_task == "Opposition Report" and "Team" in df_normalized.columns:
        team_names = df_normalized["Team"].dropna().unique()
        selected_team = st.sidebar.selectbox("Select opposition team for report", team_names)
        subject = selected_team
        data_to_send = df_normalized[df_normalized["Team"] == selected_team]
    else:
        subject = "the match"
        data_to_send = df_normalized

    # Improved system prompts
    if user_task == "Player Report":
        system_prompt = (
            "You are a senior professional football scout preparing reports for coaching and recruitment staff. "
            "Your writing should be concise, insightful, and focused on decision-making. Evaluate players in terms of:\n"
            "- Technical ability\n- Tactical intelligence\n- Physical performance\n- Psychological attributes\n\n"
            "Use analytical language but avoid unnecessary jargon. Summarize performance without just listing raw stats."
        )
    elif user_task == "Opposition Report":
        system_prompt = (
            "You are a tactical analyst preparing an opposition scouting report for coaches. "
            "Your focus is on team shape, strengths, weaknesses, key players, transitions, set pieces, and tendencies. "
            "Use bullet points where appropriate and provide actionable insights backed by data."
        )
    elif user_task == "Match Report":
        system_prompt = (
            "You are a match analyst writing a post-match report for technical staff. "
            "Summarize key events, trends, standout performers, and tactical observations using the provided match data. "
            "Be objective, insightful, and provide interpretation rather than raw numbers."
        )

    # Get available columns info for the prompt
    available_columns_info = viz_utils.get_available_columns_info()
    
    # Build user prompt with column information
    user_prompt = build_prompt(user_task, data_to_send.to_dict(orient='records'), visuals_enabled, available_columns_info)

    # Warn if visual columns are missing
    required_cols = {"x", "y", "end_x", "end_y"}
    if visuals_enabled and not required_cols.issubset(set(df_normalized.columns)):
        st.warning("⚠️ Visualization may fail — your data may be missing key coordinate columns like 'x', 'y', 'end_x', or 'end_y'.")

    if st.button("🧠 Generate Report"):
        # Create a placeholder for streaming output
        report_placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Generating report..."):
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY"),
            )
            
            # Stream the response
            try:
                stream = client.chat.completions.create(
                    model="meta-llama/llama-3-70b-instruct",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    stream=True
                )
                
                # Display streaming response
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        report_placeholder.markdown(full_response + "▌")
                        time.sleep(0.01)  # Small delay for better UX
                
                # Final display without cursor
                report_placeholder.markdown(full_response)
                
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
        
        # The report is already displayed in the streaming placeholder above
        # No need to display it again
        
        # Download button for report
        st.download_button(
            label="Download Report as TXT",
            data=full_response,
            file_name=f"{user_task.replace(' ', '_').lower()}_{subject}.txt",
            mime="text/plain"
        )

        # Handle visualizations if enabled
        if visuals_enabled:
            st.markdown("### 📊 Suggested Visualizations")
            
            # Extract code blocks from the response
            code_blocks = viz_utils.extract_code_blocks(full_response)
            
            if not code_blocks:
                st.info("No visualization suggestions found in the response.")
            else:
                for i, code in enumerate(code_blocks):
                    st.markdown(f"#### Suggested Visualization {i+1}")
                    
                    # Show the suggested code as a reference
                    with st.expander(f"View suggested code for visualization {i+1}"):
                        st.code(code, language="python")
                    
                    st.info("💡 This is a suggested visualization code block. You can copy and modify it in your own environment if needed.")
                    
                    st.divider()

else:
    st.info("Please upload a CSV file to get started.")
