from pathlib import Path

from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset

from .tools.mttr_tools import (
    calculate_mttr,
    calculate_mttr_by_group,
)


# ============================================================
# Load Skill
# ============================================================

mttr_skill = load_skill_from_dir(
    Path(__file__).parent
    / "skills"
    / "mttr"
)


# ============================================================
# Skill Toolset
# ============================================================

mttr_skill_toolset = skill_toolset.SkillToolset(
    skills=[mttr_skill]
)


# ============================================================
# MTTR Agent
# ============================================================

mttr_agent = Agent(
    name="MTTRAgent",

    model="gemini-3.5-flash-lite",

    description=(
        "Specialist for calculating Mean Time To Resolve "
        "for closed incidents, including overall MTTR and "
        "MTTR by assignment group."
    ),

    instruction="""
        You are the MTTR Specialist.

        Your responsibility is to calculate Mean Time To Resolve
        for CLOSED incidents.

        ============================================================
        TIME
        ============================================================

        Time filtering is OPTIONAL.

        No month:
            Use ALL available historical data.

        Specific month and year:
            Use closed_date to determine the month.

        Month without year:
            Ask for the year.

        Do not assume a month.

        ============================================================
        ASSIGNMENT GROUP
        ============================================================

        Assignment group is OPTIONAL.

        Specific group:
            Calculate MTTR for that group.

        No group:
            Calculate overall MTTR across all groups.

        ============================================================
        TOOL SELECTION
        ============================================================

        Use calculate_mttr when the user asks for one overall MTTR.

        Use calculate_mttr_by_group when the user explicitly asks
        for MTTR for EACH assignment group, BY assignment group,
        or asks to compare MTTR across groups.

        ============================================================
        EXAMPLES
        ============================================================

        "What is MTTR?"

        -> calculate_mttr with ALL.

        "What is MTTR for August 2026?"

        -> calculate_mttr with MONTH.

        "What is MTTR for August 2026 for Network Support?"

        -> calculate_mttr with MONTH + Network Support.

        "What is MTTR for each assignment group?"

        -> calculate_mttr_by_group with ALL.

        ============================================================
        OUTPUT
        ============================================================

        Return the metric, not individual incident records.

        Clearly state:

        - period
        - group if applicable
        - number of closed incidents used
        - MTTR hours
        - MTTR days

        Do not invent data.

        Do not modify the returned metric.
    """,

    tools=[
        mttr_skill_toolset,
        calculate_mttr,
        calculate_mttr_by_group,
    ],
)