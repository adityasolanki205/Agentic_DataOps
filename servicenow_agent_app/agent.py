# agent.py
import os
import google.auth
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig
from tools.agent_tools import mttr_skill_tool, aging_skill_tool, execute_sql_tool

# Load environment variables
load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")

credentials, _ = google.auth.default(quota_project_id=PROJECT_ID)

open_incident_agent = Agent(
    name="OpenIncidentAgent",
    model="gemini-3.5-flash-lite",
    instruction="You handle open incidents. Use `calculate_open_incident_aging` to find aging tickets.",
    tools=[aging_skill_tool]
)

closed_incident_agent = Agent(
    name="ClosedIncidentAgent",
    model="gemini-3.5-flash-lite",
    instruction="You handle closed incidents. Use `calculate_mttr_by_group` to get resolution speeds.",
    tools=[mttr_skill_tool]
)

bq_toolset = BigQueryToolset(credentials_config=BigQueryCredentialsConfig(credentials=credentials))
analytics_agent = Agent(
    name="AnalyticsAgent",
    model="gemini-3.5-flash-lite",
    instruction=f"Execute SQL against `{PROJECT_ID}.servicenow_itsm.incidents` for general analytics.",
    tools=[execute_sql_tool]
)

root_agent = Agent(
    name="ServiceNowMasterAgent",
    model="gemini-3.5-flash-lite",
    instruction="""
    You are the Lead ServiceNow ITSM Operations AI. Delegate requests:
    - Open tickets/aging -> OpenIncidentAgent
    - MTTR/closed tickets -> ClosedIncidentAgent
    - Custom SQL data/tables -> AnalyticsAgent
    """,
    sub_agents=[open_incident_agent, closed_incident_agent, analytics_agent]
)