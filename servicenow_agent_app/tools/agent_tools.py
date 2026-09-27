# servicenow_agent_app/tools/agent_tools.py
from google.adk.tools import FunctionTool
from skills.incidents_skills import calculate_mttr_by_group, calculate_open_incident_aging, execute_bigquery_sql

mttr_skill_tool = FunctionTool(calculate_mttr_by_group)

aging_skill_tool = FunctionTool(calculate_open_incident_aging)

execute_sql_tool = FunctionTool(execute_bigquery_sql)