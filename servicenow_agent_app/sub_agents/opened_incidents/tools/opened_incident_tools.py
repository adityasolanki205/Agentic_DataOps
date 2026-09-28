from datetime import datetime, timezone
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


# ============================================================
# Helper: Build date filter
# ============================================================

def _build_date_filter(
    time_scope: str,
    month: int = None,
    year: int = None,
):
    """
    Builds the opened_date filter and BigQuery parameters.
    """

    time_scope = time_scope.upper().strip()

    if time_scope not in {"MONTH", "ALL"}:
        raise ValueError("time_scope must be MONTH or ALL.")

    conditions = []
    parameters = []

    if time_scope == "MONTH":

        if month is None or year is None:
            raise ValueError(
                "For MONTH scope, both month and year are required."
            )

        if month < 1 or month > 12:
            raise ValueError(
                "month must be between 1 and 12."
            )

        if year < 2000 or year > 2100:
            raise ValueError(
                "year must be a valid four-digit year."
            )

        start_date = datetime(
            year,
            month,
            1,
            tzinfo=timezone.utc
        )

        if month == 12:
            end_date = datetime(
                year + 1,
                1,
                1,
                tzinfo=timezone.utc
            )
        else:
            end_date = datetime(
                year,
                month + 1,
                1,
                tzinfo=timezone.utc
            )

        conditions.append(
            "opened_date >= @start_date"
        )

        conditions.append(
            "opened_date < @end_date"
        )

        parameters.extend([
            bigquery.ScalarQueryParameter(
                "start_date",
                "TIMESTAMP",
                start_date
            ),
            bigquery.ScalarQueryParameter(
                "end_date",
                "TIMESTAMP",
                end_date
            )
        ])

    return conditions, parameters


# ============================================================
# Tool 1: COUNT opened incidents
# ============================================================

def count_opened_incidents(
    time_scope: str,
    month: int = None,
    year: int = None,
    assignment_group: str = None,
) -> dict:
    """
    Returns only the count of incidents opened during the
    requested period.

    Use this when the user asks:
    - how many
    - total
    - count
    - number of opened incidents
    """

    try:

        if not BQ_PROJECT_ID:
            return {
                "status": "ERROR",
                "message": "BQ_PROJECT_ID is not configured."
            }

        client = bigquery.Client(
            project=BQ_PROJECT_ID
        )

        table_name = (
            f"`{BQ_PROJECT_ID}."
            f"{BQ_DATASET_ID}."
            f"{BQ_TABLE_ID}`"
        )

        conditions, parameters = _build_date_filter(
            time_scope,
            month,
            year
        )

        # Assignment group filter
        if assignment_group:

            conditions.append(
                "LOWER(assignment_group) = "
                "LOWER(@assignment_group)"
            )

            parameters.append(
                bigquery.ScalarQueryParameter(
                    "assignment_group",
                    "STRING",
                    assignment_group
                )
            )

        # Build WHERE clause safely
        if conditions:

            where_clause = (
                "WHERE " +
                " AND ".join(conditions)
            )

        else:

            where_clause = ""

        query = f"""
            SELECT
                COUNT(*) AS total_opened_incidents
            FROM {table_name}
            {where_clause}
        """

        config = bigquery.QueryJobConfig(
            query_parameters=parameters
        )

        result = client.query(
            query,
            job_config=config
        ).result()

        row = list(result)[0]

        total = int(
            row["total_opened_incidents"]
        )

        period = (
            f"{year}-{month:02d}"
            if time_scope.upper() == "MONTH"
            else "ALL AVAILABLE DATA"
        )

        return {
            "status": "SUCCESS",
            "period": period,
            "assignment_group": (
                assignment_group
                if assignment_group
                else "ALL GROUPS"
            ),
            "total_opened_incidents": total
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "message": str(e)
        }


# ============================================================
# Tool 2: Get opened incident DETAILS
# ============================================================

def get_opened_incident_details(
    time_scope: str,
    month: int = None,
    year: int = None,
    assignment_group: str = None,
    limit: int = 100,
) -> dict:
    """
    Returns actual incident records.

    Use this ONLY when the user explicitly requests:
    - incident details
    - incident records
    - tickets
    - incident IDs
    - a list of incidents
    """

    try:

        if not BQ_PROJECT_ID:
            return {
                "status": "ERROR",
                "message": "BQ_PROJECT_ID is not configured."
            }

        client = bigquery.Client(
            project=BQ_PROJECT_ID
        )

        table_name = (
            f"`{BQ_PROJECT_ID}."
            f"{BQ_DATASET_ID}."
            f"{BQ_TABLE_ID}`"
        )

        conditions, parameters = _build_date_filter(
            time_scope,
            month,
            year
        )

        # Assignment group
        if assignment_group:

            conditions.append(
                "LOWER(assignment_group) = "
                "LOWER(@assignment_group)"
            )

            parameters.append(
                bigquery.ScalarQueryParameter(
                    "assignment_group",
                    "STRING",
                    assignment_group
                )
            )

        if conditions:

            where_clause = (
                "WHERE " +
                " AND ".join(conditions)
            )

        else:

            where_clause = ""

        # Keep result size controlled
        limit = max(
            1,
            min(limit, 500)
        )

        query = f"""
            SELECT
                incident_id,
                opened_date,
                closed_date,
                status,
                assignment_group,
                assignee,
                category,
                priority,
                short_description
            FROM {table_name}
            {where_clause}
            ORDER BY opened_date DESC
            LIMIT @limit
        """

        parameters.append(
            bigquery.ScalarQueryParameter(
                "limit",
                "INT64",
                limit
            )
        )

        config = bigquery.QueryJobConfig(
            query_parameters=parameters
        )

        result = client.query(
            query,
            job_config=config
        ).result()

        incidents = []

        for row in result:

            incidents.append(
                {
                    "incident_id": row["incident_id"],
                    "opened_date": (
                        row["opened_date"].isoformat()
                        if row["opened_date"]
                        else None
                    ),
                    "closed_date": (
                        row["closed_date"].isoformat()
                        if row["closed_date"]
                        else None
                    ),
                    "status": row["status"],
                    "assignment_group": (
                        row["assignment_group"]
                    ),
                    "assignee": row["assignee"],
                    "category": row["category"],
                    "priority": row["priority"],
                    "short_description": (
                        row["short_description"]
                    ),
                }
            )

        period = (
            f"{year}-{month:02d}"
            if time_scope.upper() == "MONTH"
            else "ALL AVAILABLE DATA"
        )

        return {
            "status": "SUCCESS",
            "period": period,
            "assignment_group": (
                assignment_group
                if assignment_group
                else "ALL GROUPS"
            ),
            "returned_incidents": len(incidents),
            "limit": limit,
            "incidents": incidents
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "message": str(e)
        }