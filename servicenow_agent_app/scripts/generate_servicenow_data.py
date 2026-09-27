import random
from datetime import datetime, timedelta
import pandas as pd
from google.cloud import bigquery

# Project Configuration
PROJECT_ID = "solar-dialect-264808"  # Replace with your GCP project ID
DATASET_ID = "servicenow_itsm"
TABLE_ID = "incidents"

ASSIGNMENT_GROUPS = [
    "Database Admin", "Network Support", "Service Desk", 
    "Cloud Infrastructure", "Cyber Security", "Application Dev"
]

ASSIGNEES = {
    "Database Admin": ["Alice M.", "Bob K."],
    "Network Support": ["Charlie D.", "Diana P."],
    "Service Desk": ["Evan R.", "Fiona L."],
    "Cloud Infrastructure": ["George B.", "Hannah T."],
    "Cyber Security": ["Ian W.", "Julia S."],
    "Application Dev": ["Kevin V.", "Laura C."]
}

CATEGORIES = ["Hardware", "Software", "Network", "Database", "Security"]
PRIORITIES = ["1 - Critical", "2 - High", "3 - Moderate", "4 - Low"]

def generate_incidents(num_records=10000):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    data = []
    
    for i in range(1, num_records + 1):
        inc_id = f"INC{str(i).zfill(7)}"
        
        # Distribute opened dates evenly over 6 months
        random_days = random.uniform(0, 180)
        opened_at = start_date + timedelta(days=random_days)
        
        group = random.choice(ASSIGNMENT_GROUPS)
        assignee = random.choice(ASSIGNEES[group])
        category = random.choice(CATEGORIES)
        priority = random.choice(PRIORITIES)
        
        # Decide status based on probability
        # 80% Closed, 20% Open (New / In Progress / On Hold)
        is_closed = random.random() < 0.80
        
        if is_closed:
            status = "Closed"
            # Resolution time between 15 mins to 14 days
            resolution_hours = random.expovariate(1 / 36.0)  # Mean ~36 hours
            closed_at = opened_at + timedelta(hours=max(0.25, resolution_hours))
            # Ensure closed date doesn't exceed current date
            if closed_at > end_date:
                closed_at = end_date
        else:
            status = random.choice(["New", "In Progress", "On Hold"])
            closed_at = None
            
        data.append({
            "incident_id": inc_id,
            "opened_date": opened_at,
            "closed_date": closed_at,
            "status": status,
            "assignment_group": group,
            "assignee": assignee,
            "category": category,
            "priority": priority,
            "short_description": f"Issue related to {category.lower()} in {group}"
        })
        
    return pd.DataFrame(data)

def upload_to_bigquery(df):
    client = bigquery.Client(project=PROJECT_ID)
    
    # Create dataset if not exists
    dataset_ref = client.dataset(DATASET_ID)
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = "US"
    client.create_dataset(dataset, exists_ok=True)
    
    table_ref = dataset_ref.table(TABLE_ID)
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()  # Wait for completion
    print(f"Successfully loaded {len(df)} rows to {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}")

if __name__ == "__main__":
    print("Generating ServiceNow incidents dataset...")
    df_incidents = generate_incidents(100000)
    upload_to_bigquery(df_incidents)
