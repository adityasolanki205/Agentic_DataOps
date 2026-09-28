from google.adk import Agent


mttr_agent = Agent(
    name="MTTRAgent",

    model="gemini-3.5-flash-lite",

    description=(
        "Specialist for calculating Mean Time To Resolve. "
        "The capability is currently under development."
    ),

    instruction="""
You are the MTTR Specialist.

The MTTR capability is currently under development.

Do not invent MTTR values.

Tell the user that this capability has not yet been implemented.
""",
)