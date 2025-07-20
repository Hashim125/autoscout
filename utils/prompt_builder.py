def build_prompt(report_type, sample_data, visuals_enabled=False, available_columns_info="", file_type=None):
    """
    Constructs a tailored prompt for GPT based on report type and match/player data.
    """
    if file_type == "scout_report":
        base_instruction = f"""
You are a professional football staff member working for a professional football club.
You have been provided with a table of existing scout reports or qualitative observations (not raw event data).
Your job is to synthesize, summarize, and rephrase the key insights for a {report_type.lower()}.

IMPORTANT:
- Do NOT copy-paste the text verbatim from the data.
- Instead, extract the most important points, combine similar observations, and write a concise, professional summary in your own words.
- Avoid repetition and focus on actionable insights.
- Do NOT include any code, code blocks, or visualization sections in the written report.

AVAILABLE DATA COLUMNS:
{available_columns_info}

DATA TO ANALYZE:
{sample_data}
"""
    else:
        base_instruction = f"""
You are a professional football staff member working for a professional football club.
Use the data below to write a comprehensive, insightful, and professional {report_type.lower()}.

AVAILABLE DATA COLUMNS:
{available_columns_info}

WRITTEN REPORT REQUIREMENTS:
- Write a detailed, professional {report_type.lower()} in the style of a football scout/analyst/coach
- Focus on performance insights, key stats, strengths, weaknesses, and tactical observations
- Use bullet points where appropriate for clarity
- Keep the tone analytical but accessible
- Avoid just listing raw numbers — interpret and explain their meaning
- Provide actionable insights and recommendations
- Structure your report with clear sections and headings
- **DO NOT include any Python code, code blocks, or visualization sections/headings in the written report.**
- **DO NOT use headings like 'Visualization', 'Visualization 1', or similar in the written report.**
- **DO NOT include any code blocks in the written report.**

DATA TO ANALYZE:
{sample_data}
"""

    if visuals_enabled:
        viz_instruction = """

## SUGGESTED VISUALIZATIONS
After completing your written report above, generate 1-2 relevant matplotlib/mplsoccer visualizations that support your analysis.

VISUALIZATION GUIDELINES:
- Use ONLY the columns listed above - do not reference non-existent columns
- Do NOT import any modules (plt, Pitch, numpy, pandas are already available)
- Output each visualization as a complete Python code block using ```python
- Focus on meaningful insights: heatmaps, pass maps, shot locations, etc.
- Ensure code is complete and executable
- Use the DataFrame 'df' as your data source
- **DO NOT embed code or code blocks in the written report.**
- **DO NOT use 'Visualization' headings in the written report. Only use them after the '## SUGGESTED VISUALIZATIONS' marker.**

EXAMPLE CODE BLOCK (after the report):
```python
# Create pitch
pitch = Pitch()
fig, ax = pitch.draw()
# Your visualization code here using df['column_name']
plt.show()
```

RESPONSE FORMAT:
1. Complete written report (detailed analysis, NO code or visualization sections/headings)
2. After the report, start a new section with '## SUGGESTED VISUALIZATIONS' and output only the code blocks there.
"""
        base_instruction += viz_instruction
    else:
        base_instruction += """

RESPONSE FORMAT:
Complete written report only - no code blocks or visualization sections needed.
"""

    return base_instruction
