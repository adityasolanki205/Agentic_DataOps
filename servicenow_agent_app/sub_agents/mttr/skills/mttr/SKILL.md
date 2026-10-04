---
name: mttr
description: Calculate Mean Time To Resolve for closed incidents with optional time and assignment-group filtering.
---

# MTTR Skill

## Purpose

Calculate Mean Time To Resolve (MTTR) for closed incidents.

## Closed Incident Definition

A closed incident has:

status = 'Closed'

Only closed incidents are included.

## MTTR Definition

For each eligible incident:

resolution time = closed_date - opened_date

MTTR is the average resolution time.

The calculation should preserve timestamp precision.

## Time Filter

Time is OPTIONAL.

If the user provides month and year:

Use closed_date to determine the month.

If the user does not provide a month:

Use ALL available historical data.

Do not ask for a month.

If the user gives a month without a year:

Ask for the year.

## Assignment Group

Assignment group is OPTIONAL.

If a specific assignment group is provided:

Calculate MTTR for that group.

If no group is provided:

Calculate overall MTTR across all groups.

Do not invent assignment groups.

## Overall MTTR

Use the overall MTTR capability when the user asks:

- What is MTTR?
- What is the mean time to resolve?
- What is our average resolution time?
- What is MTTR for August 2026?
- What is MTTR for Network Support?

## MTTR By Assignment Group

Use the grouped capability when the user asks:

- What is MTTR for each assignment group?
- Show MTTR by assignment group.
- Compare MTTR across assignment groups.
- Give me MTTR associated with each assignment group.

## Examples

"What is MTTR?"

Means:

- all closed incidents
- all available history
- all groups

"What is MTTR for August 2026?"

Means:

- status = Closed
- closed_date in August 2026
- all groups

"What is MTTR for August 2026 for Network Support?"

Means:

- status = Closed
- closed_date in August 2026
- assignment_group = Network Support

"What is MTTR for each assignment group?"

Means:

- status = Closed
- all available history
- group by assignment_group

## Output

MTTR is a metric.

Do not return individual incident records unless the user
explicitly requests the underlying incidents.

Return:

- period
- assignment group if applicable
- closed incident count used
- MTTR in hours
- MTTR in days when useful

Do not invent values.