---
name: aging
description: Calculate average aging of currently open incidents using optional month, year, and assignment-group filters.
---

# Average Aging Skill

## Purpose

Calculate the average aging of currently open incidents.

## Definition of Currently Open

An incident is currently open when its status is one of:

- New
- In Progress
- On Hold

An incident with:

status = 'Closed'

is not currently open.

## Aging Definition

For a currently open incident:

aging = CURRENT_TIMESTAMP() - opened_date

Average aging is the average of the aging of all eligible
currently open incidents.

## Time Filter

Time is OPTIONAL.

If the user specifies a month and year:

- Use opened_date to determine the month.

If the user does not specify a month:

- Use ALL available history.

Never force the user to provide a month.

If a month is provided without a year, ask for the year.

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

- Restrict the calculation to that assignment group.

If not supplied:

- Include all assignment groups.

Never invent an assignment group.

## Examples

"What is the average aging of open incidents?"

Means:

- currently open incidents
- all available history
- all assignment groups

"What is the average aging of open incidents for August 2026?"

Means:

- status IN ('New', 'In Progress', 'On Hold')
- opened_date in August 2026
- all assignment groups

"What is the average aging for Network Support?"

Means:

- currently open incidents
- all available history
- assignment_group = Network Support

"What is the average aging for August 2026 for Network Support?"

Means:

- status IN ('New', 'In Progress', 'On Hold')
- opened_date in August 2026
- assignment_group = Network Support

## Output

Return:

- requested period
- assignment group, if supplied
- number of currently open incidents included
- average aging

Use days as the primary business-friendly unit.

Example:

"Average aging is 18.4 days."

## No Matching Data

If there are no matching currently open incidents:

Clearly state that no matching open incidents were found.

Do not return an invented result.

## Important Distinction

This skill calculates the aging of incidents that are currently open.

It is different from:

"incidents opened during a month."

Do not use status to determine whether an incident was opened
during a month.

Do not include Closed incidents.

## Monthly Interpretation

For this first version:

"average aging for August 2026"

means:

currently open incidents whose opened_date falls in August 2026.

This definition should remain consistent across the application.