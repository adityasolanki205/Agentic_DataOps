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


OPEN_STATUSES = [
    "New",
    "In Progress",
    "On Hold",
]


# ============================================================
# Helper: Build opened_date filter
# ============================================================

def _build_opened_date_filter(
    time_scope: str = "ALL",
    month: int = None,
    year: int = None,
):
    """
    Build an opened_date filter.

    MONTH:
        Filter by month and year.

    ALL:
        No date filter.
    """

    time_scope = (time_scope or "ALL").upper().strip()

    if time_scope not in {"MONTH", "ALL"}:
        raise ValueError(
            "time_scope must be MONTH or ALL."
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
# Tool 1: Overall Average Aging
# ============================================================

def calculate_open_incident_aging(
    time_scope: str = "ALL",
    month: int = None,
    year: int = None,
    assignment_group: str = None,
) -> dict:
    """
    Calculate average aging of currently open incidents.

    Currently open statuses:

    - New
    - In Progress
    - On Hold

    If no month is supplied:
        Use all available history.

    If a month is supplied:
        opened_date determines the month.

    Assignment group is optional.
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
            "status IN UNNEST(@open_statuses)",
            "opened_date IS NOT NULL"
        ]

        parameters = [
            bigquery.ArrayQueryParameter(
                "open_statuses",
                "STRING",
                OPEN_STATUSES
            )
        ]

        date_conditions, date_parameters = (
            _build_opened_date_filter(
                time_scope,
                month,
                year
            )
        )

        conditions.extend(date_conditions)
        parameters.extend(date_parameters)

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

        query = f"""
            SELECT
                COUNT(*) AS open_incident_count,

                AVG(
                    TIMESTAMP_DIFF(
                        CURRENT_TIMESTAMP(),
                        opened_date,
                        SECOND
                    )
                ) AS avg_age_seconds

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

        incident_count = int(
            row["open_incident_count"]
        )

        period = (
            f"{year}-{month:02d}"
            if time_scope.upper() == "MONTH"
            else "ALL AVAILABLE DATA"
        )

        if incident_count == 0:

            return {
                "status": "SUCCESS",
                "period": period,
                "assignment_group": (
                    assignment_group
                    if assignment_group
                    else "ALL GROUPS"
                ),
                "open_incident_count": 0,
                "message": "No matching open incidents found."
            }

        avg_age_seconds = float(
            row["avg_age_seconds"]
        )

        avg_age_days = (
            avg_age_seconds / 86400
        )

        return {
            "status": "SUCCESS",
            "period": period,
            "assignment_group": (
                assignment_group
                if assignment_group
                else "ALL GROUPS"
            ),
            "open_incident_count": incident_count,
            "average_aging_days": round(
                avg_age_days,
                2
            )
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "message": str(e)
        }


# ============================================================
# Tool 2: Average Aging by Assignment Group
# ============================================================

def calculate_open_incident_aging_by_group(
    time_scope: str = "ALL",
    month: int = None,
    year: int = None,
) -> dict:
    """
    Calculate average aging for each assignment group.

    Only currently open incidents are included.
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
            "status IN UNNEST(@open_statuses)",
            "opened_date IS NOT NULL"
        ]

        parameters = [
            bigquery.ArrayQueryParameter(
                "open_statuses",
                "STRING",
                OPEN_STATUSES
            )
        ]

        date_conditions, date_parameters = (
            _build_opened_date_filter(
                time_scope,
                month,
                year
            )
        )

        conditions.extend(date_conditions)
        parameters.extend(date_parameters)

        where_clause = (
            "WHERE " +
            " AND ".join(conditions)
        )

        query = f"""
            SELECT
                assignment_group,
                COUNT(*) AS open_incident_count,

                AVG(
                    TIMESTAMP_DIFF(
                        CURRENT_TIMESTAMP(),
                        opened_date,
                        SECOND
                    )
                ) AS avg_age_seconds

            FROM {table_name}

            {where_clause}

            GROUP BY assignment_group

            ORDER BY avg_age_seconds DESC
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

            seconds = float(
                row["avg_age_seconds"]
            )

            groups.append(
                {
                    "assignment_group": (
                        row["assignment_group"]
                    ),
                    "open_incident_count": int(
                        row["open_incident_count"]
                    ),
                    "average_aging_days": round(
                        seconds / 86400,
                        2
                    )
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
            "aging_by_assignment_group": groups
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "message": str(e)
        }