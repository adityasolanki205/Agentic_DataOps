# skills/incident_skills.py
import os
from dotenv import load_dotenv
from google.cloud import bigquery
import pandas as pd


# Load environment variables from .env
load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_ID = "servicenow_itsm"
TABLE_ID = "incidents"

def calculate_mttr_by_group(assignment_group: str = None) -> str:
    """Computes Mean Time To Resolve (MTTR) in hours and days for closed incidents."""
    if not PROJECT_ID:
        return "Error: PROJECT_ID is not set in the environment."
        
    client = bigquery.Client(project=PROJECT_ID)
    
    where_clause = "WHERE status = 'Closed'"
    if assignment_group:
        where_clause += f" AND LOWER(assignment_group) = LOWER('{assignment_group}')"
        
    query = f"""
        SELECT 
            assignment_group,
            COUNT(incident_id) as total_closed_tickets,
            ROUND(AVG(TIMESTAMP_DIFF(closed_date, opened_date, HOUR)), 2) as avg_mttr_hours,
            ROUND(AVG(TIMESTAMP_DIFF(closed_date, opened_date, DAY)), 2) as avg_mttr_days
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        {where_clause}
        GROUP BY assignment_group
        ORDER BY avg_mttr_hours DESC
    """
    df = client.query(query).to_dataframe()
    
    if df.empty:
        target = assignment_group if assignment_group else "any group"
        return f"No closed incidents found for {target}."
    
    # If a specific group was requested, return a single summary
    if assignment_group:
        row = df.iloc[0]
        return (
            f"=== MTTR Metrics for {row['assignment_group']} ===\n"
            f"- Total Closed Incidents: {row['total_closed_tickets']}\n"
            f"- Average MTTR: {row['avg_mttr_hours']} hours ({row['avg_mttr_days']} days)"
        )
    
    # If no group was requested, return the full table of all groups
    return "=== MTTR Metrics for All Groups ===\n" + df.to_string(index=False)

def calculate_open_incident_aging(assignment_group: str = None, top_n: int = 10) -> str:
    """Calculates aging (days since opened) for open incidents and average age per s."""
    if not PROJECT_ID:
        return "Error: PROJECT_ID is not set in the environment."
        
    client = bigquery.Client(project=PROJECT_ID)
    
    where_clause = "WHERE status != 'Closed'"
    if assignment_group:
        where_clause += f" AND LOWER(assignment_group) = LOWER('{assignment_group}')"
        
    # Query 1: Get the average aging aggregated by group
    agg_query = f"""
        SELECT 
            assignment_group,
            COUNT(incident_id) as total_open_tickets,
            ROUND(AVG(TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), opened_date, DAY)), 2) as avg_age_days
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        {where_clause}
        GROUP BY assignment_group
        ORDER BY avg_age_days DESC
    """
    
    # Query 2: Get the specific oldest tickets
    details_query = f"""
        SELECT 
            incident_id, status, priority, assignment_group, assignee,
            opened_date, TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), opened_date, DAY) as age_days
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        {where_clause}
        ORDER BY age_days DESC
        LIMIT {top_n}
    """
    
    df_agg = client.query(agg_query).to_dataframe()
    df_details = client.query(details_query).to_dataframe()
    
    if df_agg.empty:
        target = assignment_group if assignment_group else "any group"
        return f"No open incidents found for {target}."
    
    df_details['opened_date'] = pd.to_datetime(df_details['opened_date']).dt.strftime('%Y-%m-%d')
    title = f"for {assignment_group}" if assignment_group else "for All Groups"
    
    result = f"=== Average Open Incident Aging {title} ===\n"
    result += df_agg.to_string(index=False) + "\n\n"
    result += f"=== Top {len(df_details)} Oldest Open Incidents ===\n"
    result += df_details.to_string(index=False)
    
    return result

def execute_bigquery_sql(sql_query: str) -> str:
    """Executes a standard SQL query against BigQuery and returns the results as a string."""
    if not PROJECT_ID:
        return "Error: PROJECT_ID is not set in the environment."
        
    client = bigquery.Client(project=PROJECT_ID)
    try:
        # Run query and convert to a Markdown table format for the agent
        df = client.query(sql_query).to_dataframe()
        if df.empty:
            return "Query executed successfully but returned no results."
        return df.to_markdown(index=False)
    except Exception as e:
        return f"SQL Execution Error: {str(e)}"