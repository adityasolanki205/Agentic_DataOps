import os

from dotenv import load_dotenv
from google.cloud import bigquery


load_dotenv()

BQ_PROJECT_ID = os.getenv(
    "BQ_PROJECT_ID",
    os.getenv("PROJECT_ID")
)

BQ_DATASET_ID = os.getenv(
    "BQ_DATASET_ID",
    "servicenow_itsm"
)

BQ_TABLE_ID = os.getenv(
    "BQ_TABLE_ID",
    "incidents"
)


OPEN_STATUSES = [
    "New",
    "In Progress",
    "On Hold",
]


def count_all_incidents() -> dict:
    """
    Returns the total number of incidents in the table.

    No date, status, or assignment-group filter is applied.
    """

    try:
        if not BQ_PROJECT_ID:
            return {
                "status": "ERROR",
                "message": "BQ_PROJECT_ID is not configured."
            }

        client = bigquery.Client(project=BQ_PROJECT_ID)

        table_name = (
            f"`{BQ_PROJECT_ID}."
            f"{BQ_DATASET_ID}."
            f"{BQ_TABLE_ID}`"
        )

        query = f"""
            SELECT COUNT(*) AS total_incidents
            FROM {table_name}
        """

        result = client.query(query).result()
        row = list(result)[0]

        return {
            "status": "SUCCESS",
            "total_incidents": int(row["total_incidents"])
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e)
        }


def count_open_incidents_by_group() -> dict:
    """
    Returns the count of currently open incidents for each
    assignment group.

    Currently open statuses:
    New
    In Progress
    On Hold
    """

    try:
        if not BQ_PROJECT_ID:
            return {
                "status": "ERROR",
                "message": "BQ_PROJECT_ID is not configured."
            }

        client = bigquery.Client(project=BQ_PROJECT_ID)

        table_name = (
            f"`{BQ_PROJECT_ID}."
            f"{BQ_DATASET_ID}."
            f"{BQ_TABLE_ID}`"
        )

        query = f"""
            SELECT
                assignment_group,
                COUNT(*) AS open_incident_count
            FROM {table_name}
            WHERE status IN UNNEST(@open_statuses)
            GROUP BY assignment_group
            ORDER BY open_incident_count DESC
        """

        config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ArrayQueryParameter(
                    "open_statuses",
                    "STRING",
                    OPEN_STATUSES
                )
            ]
        )

        result = client.query(
            query,
            job_config=config
        ).result()

        groups = []

        for row in result:
            groups.append({
                "assignment_group": row["assignment_group"],
                "open_incident_count": int(
                    row["open_incident_count"]
                )
            })

        return {
            "status": "SUCCESS",
            "period": "ALL AVAILABLE DATA",
            "open_incidents_by_assignment_group": groups
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e)
        }