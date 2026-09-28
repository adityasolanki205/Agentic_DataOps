from datetime import datetime, timezone
import os

from dotenv import load_dotenv
from google.cloud import bigquery


load_dotenv()

# ============================================================
# Configuration
# ============================================================

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
# Helper: Build closed_date filter
# ============================================================

def _build_date_filter(
    time_scope: str = "ALL",
    month: int = None,
    year: int = None,
):
    """
    Builds the closed_date filter.

    MONTH:
        Requires month and year.

    ALL:
        No date filter is applied.
    """

    time_scope = (time_scope or "ALL").upper().strip()

    if time_scope not in {"MONTH", "ALL"}:
        raise ValueError(
            "time_scope must be either MONTH or ALL."
        )

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
            "closed_date >= @start_date"
        )

        conditions.append(
            "closed_date < @end_date"
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
# Tool 1: Count ALL closed incidents
# ============================================================

def count_closed_incidents(
    time_scope: str = "ALL",
    month: int = None,
    year: int = None,
    assignment_group: str = None,
) -> dict:
    """
    Count closed incidents.

    If no time scope is supplied, all available historical
    closed incidents are counted.

    If no assignment group is supplied, all groups are included.

    Use this for questions such as:
    - How many incidents were closed?
    - What is the total number of closed incidents?
    - Closed incident count for August 2026
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

        conditions = [
            "status = 'Closed'"
        ]

        date_conditions, parameters = _build_date_filter(
            time_scope,
            month,
            year
        )

        conditions.extend(date_conditions)

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

        # Important:
        # WHERE is added only after we have conditions.
        where_clause = (
            "WHERE " +
            " AND ".join(conditions)
        )

        query = f"""
            SELECT
                COUNT(*) AS total_closed_incidents
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
            row["total_closed_incidents"]
        )

        if (time_scope or "ALL").upper() == "MONTH":
            period = f"{year}-{month:02d}"
        else:
            period = "ALL AVAILABLE DATA"

        return {
            "status": "SUCCESS",
            "period": period,
            "assignment_group": (
                assignment_group
                if assignment_group
                else "ALL GROUPS"
            ),
            "total_closed_incidents": total
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "message": str(e)
        }


# ============================================================
# Tool 2: Closed incidents by Assignment Group
# ============================================================

def count_closed_incidents_by_group(
    time_scope: str = "ALL",
    month: int = None,
    year: int = None,
) -> dict:
    """
    Return the number of closed incidents for each
    assignment group.

    If no time scope is supplied, all available history
    is used.

    For a month, closed_date determines the month.

    Use this for questions such as:

    - How many closed incidents does each assignment group have?
    - Show closed incident count by assignment group.
    - Give me closed incidents associated with each group.
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

        conditions = [
            "status = 'Closed'"
        ]

        date_conditions, parameters = _build_date_filter(
            time_scope,
            month,
            year
        )

        conditions.extend(date_conditions)

        where_clause = (
            "WHERE " +
            " AND ".join(conditions)
        )

        query = f"""
            SELECT
                assignment_group,
                COUNT(*) AS closed_incident_count
            FROM {table_name}
            {where_clause}
            GROUP BY assignment_group
            ORDER BY closed_incident_count DESC
        """

        config = bigquery.QueryJobConfig(
            query_parameters=parameters
        )

        result = client.query(
            query,
            job_config=config
        ).result()

        groups = []

        for row in result:

            groups.append(
                {
                    "assignment_group": (
                        row["assignment_group"]
                    ),
                    "closed_incident_count": int(
                        row["closed_incident_count"]
                    )
                }
            )

        if (time_scope or "ALL").upper() == "MONTH":
            period = f"{year}-{month:02d}"
        else:
            period = "ALL AVAILABLE DATA"

        return {
            "status": "SUCCESS",
            "period": period,
            "closed_incidents_by_assignment_group": groups
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "message": str(e)
        }


# ============================================================
# Tool 3: Closed Incident DETAILS
# ============================================================

def get_closed_incident_details(
    time_scope: str = "ALL",
    month: int = None,
    year: int = None,
    assignment_group: str = None,
    limit: int = 100,
) -> dict:
    """
    Retrieve actual closed incident records.

    Use this ONLY when the user explicitly asks for:
    - details
    - records
    - tickets
    - incident IDs
    - list of closed incidents
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

        conditions = [
            "status = 'Closed'"
        ]

        date_conditions, parameters = _build_date_filter(
            time_scope,
            month,
            year
        )

        conditions.extend(date_conditions)

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

        where_clause = (
            "WHERE " +
            " AND ".join(conditions)
        )

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
            ORDER BY closed_date DESC
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

        if (time_scope or "ALL").upper() == "MONTH":
            period = f"{year}-{month:02d}"
        else:
            period = "ALL AVAILABLE DATA"

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