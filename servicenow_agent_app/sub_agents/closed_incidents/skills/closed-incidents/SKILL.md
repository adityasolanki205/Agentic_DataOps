---
name: closed-incidents
description: Analyze closed incidents using optional time and assignment-group filters, including counts, group summaries, and details.
---

# Closed Incidents Skill

## Purpose

Analyze incidents that have been closed.

## Closed Definition

A closed incident has:

status = 'Closed'

Only status = 'Closed' should be included in closed-incident
analysis.

## Time Filter

Time is OPTIONAL.

If the user gives a month and year:

Use closed_date to determine the month.

If the user does not give a month:

Use ALL available historical data.

Never force the user to provide a month.

If a month is supplied without a year, ask for the year.

## Assignment Group

Assignment group is OPTIONAL.

Valid groups:

- Application Dev
- Database Admin
- Service Desk
- Cloud Infrastructure
- Cyber Security
- Network Support

If the user supplies an assignment group:

Filter to that group.

If no assignment group is supplied:

Include all assignment groups.

Never invent an assignment group.

## COUNT

Count is the default for questions asking:

- total
- count
- number
- how many
- total closed incidents

Use:

count_closed_incidents

Examples:

"How many incidents were closed?"

"What is the total number of closed incidents?"

"How many closed incidents did Network Support have?"

Do not return individual incident records for count questions.

## GROUPED COUNT

If the user asks:

- closed incidents by assignment group
- closed incidents for each assignment group
- how many closed incidents does each group have
- closed incident count by group
- closed incidents associated with each assignment group

Use:

count_closed_incidents_by_group

Return one count for each assignment group.

Do not return individual incident records.

## DETAILS

Only return incident records when the user explicitly asks for:

- details
- records
- tickets
- incident IDs
- list of incidents
- show me the closed incidents

Use:

get_closed_incident_details

## Monthly Definition

For:

"Closed incidents in August 2026"

use:

status = 'Closed'

AND

closed_date >= 2026-08-01

AND

closed_date < 2026-09-01

## No Time Filter

For:

"How many closed incidents are there?"

interpret as:

- all available history
- all assignment groups

Do not ask for a month.

## No Assignment Group

If the user does not provide an assignment group:

include all groups.

Do not ask the user to select a group.

## Output

For count requests:

Return:

- period
- assignment group if supplied
- count

For grouped requests:

Return:

- period
- assignment-group counts

For detail requests:

Return:

- period
- assignment group if supplied
- incident records

Do not invent or modify BigQuery results.