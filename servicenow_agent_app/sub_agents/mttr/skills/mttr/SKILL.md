---
name: mttr
description: Calculate Mean Time To Resolve for closed incidents using optional month, year, and assignment-group filters.
---

# MTTR Skill

## Purpose

Calculate Mean Time To Resolve (MTTR) for closed incidents.

## Definition of Closed Incident

Only incidents with:

status = 'Closed'

are included.

Do not include:

- New
- In Progress
- On Hold

## MTTR Definition

For each closed incident:

resolution time = closed_date - opened_date

MTTR is the average resolution time across the
eligible closed incidents.

Conceptually:

MTTR = AVG(closed_date - opened_date)

The calculation should preserve timestamp precision.

## Time Filter

Time is OPTIONAL.

If the user specifies a month and year:

- Use closed_date to determine the month.

If no month is specified:

- Use ALL available historical closed incidents.

Never force the user to provide a month.

If a month is specified without a year, ask for the year.

## Assignment Group

Assignment group is OPTIONAL.

Valid assignment groups:

- Application Dev
- Database Admin
- Service Desk
- Cloud Infrastructure
- Cyber Security
- Network Support

If supplied:

- Calculate MTTR only for that assignment group.

If not supplied:

- Calculate MTTR across all assignment groups.

Never invent an assignment group.

## Examples

"What is MTTR?"

Means:

- all closed incidents
- all available history
- all assignment groups

"What is MTTR for August 2026?"

Means:

- closed incidents only
- closed_date in August 2026
- all assignment groups

"What is MTTR for August 2026 for Network Support?"

Means:

- status = Closed
- closed_date in August 2026
- assignment_group = Network Support

## Output

Return:

- requested period
- assignment group, if supplied
- number of closed incidents included
- average MTTR

Use a consistent readable unit such as:

- hours
- days

If useful, provide both.

Example:

"MTTR was 54.7 hours (2.28 days)."

## No Matching Data

If no eligible closed incidents exist:

Clearly state that no matching closed incidents were found.

Do not return an invented MTTR.

## Important

MTTR is a calculated metric.

Do not ask the user for incident details unless the user explicitly
requests the incidents contributing to the metric.

Do not calculate MTTR from non-closed incidents.

For monthly analysis, the month is determined by closed_date.