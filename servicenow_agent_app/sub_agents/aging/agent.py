from google.adk import Agent


aging_agent = Agent(
    name="AgingAgent",

    model="gemini-3.5-flash-lite",

    description=(
        "Specialist for calculating average aging of currently "
        "open incidents. The capability is currently under development."
    ),

    instruction="""
You are the Open Incident Aging Specialist.

The average-aging capability is currently under development.

Do not invent aging values.

Tell the user that this capability has not yet been implemented.
""",
)