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
# Helper: Build date filter
# ============================================================

def _build_closed_date_filter(
    time_scope: str = "ALL",
    month: int = None,
    year: int = None,
):
    """
    Build a filter based on closed_date.

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
# Tool 1: Overall MTTR
# ============================================================

def calculate_mttr(
    time_scope: str = "ALL",
    month: int = None,
    year: int = None,
    assignment_group: str = None,
) -> dict:
    """
    Calculate overall Mean Time To Resolve.

    Only CLOSED incidents with valid opened_date and closed_date
    are included.

    If no month is supplied:
        ALL available closed incidents are used.

    If no assignment group is supplied:
        ALL assignment groups are used.
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
            "status = 'Closed'",
            "opened_date IS NOT NULL",
            "closed_date IS NOT NULL"
        ]

        date_conditions, parameters = _build_closed_date_filter(
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

        query = f"""
            SELECT
                COUNT(*) AS incident_count,

                AVG(
                    TIMESTAMP_DIFF(
                        closed_date,
                        opened_date,
                        SECOND
                    )
                ) AS avg_mttr_seconds

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
            row["incident_count"]
        )

        if incident_count == 0:
            return {
                "status": "SUCCESS",
                "message": "No matching closed incidents found.",
                "period": (
                    f"{year}-{month:02d}"
                    if time_scope.upper() == "MONTH"
                    else "ALL AVAILABLE DATA"
                ),
                "assignment_group": (
                    assignment_group
                    if assignment_group
                    else "ALL GROUPS"
                ),
                "incident_count": 0
            }

        avg_mttr_seconds = float(
            row["avg_mttr_seconds"]
        )

        avg_mttr_hours = (
            avg_mttr_seconds / 3600
        )

        avg_mttr_days = (
            avg_mttr_seconds / 86400
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
            "closed_incidents_used": incident_count,
            "mttr_hours": round(
                avg_mttr_hours,
                2
            ),
            "mttr_days": round(
                avg_mttr_days,
                2
            )
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "message": str(e)
        }


# ============================================================
# Tool 2: MTTR by Assignment Group
# ============================================================

def calculate_mttr_by_group(
    time_scope: str = "ALL",
    month: int = None,
    year: int = None,
) -> dict:
    """
    Calculate MTTR separately for every assignment group.

    Only CLOSED incidents are included.

    If no month is supplied:
        ALL available history is used.

    If a month is supplied:
        closed_date determines the month.
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
            "status = 'Closed'",
            "opened_date IS NOT NULL",
            "closed_date IS NOT NULL"
        ]

        date_conditions, parameters = _build_closed_date_filter(
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
                COUNT(*) AS closed_incident_count,

                AVG(
                    TIMESTAMP_DIFF(
                        closed_date,
                        opened_date,
                        SECOND
                    )
                ) AS avg_mttr_seconds

            FROM {table_name}

            {where_clause}

            GROUP BY assignment_group

            ORDER BY avg_mttr_seconds DESC
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
                row["avg_mttr_seconds"]
            )

            groups.append(
                {
                    "assignment_group": (
                        row["assignment_group"]
                    ),
                    "closed_incident_count": int(
                        row["closed_incident_count"]
                    ),
                    "mttr_hours": round(
                        seconds / 3600,
                        2
                    ),
                    "mttr_days": round(
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
            "mttr_by_assignment_group": groups
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "message": str(e)
        }