---
name: aging
description: Calculate average aging of currently open incidents with optional time and assignment-group filters.
---

# Aging Skill

## Purpose

Calculate the average aging of currently open incidents.

## Currently Open Definition

Currently open incidents have one of these statuses:

- New
- In Progress
- On Hold

Closed incidents are excluded.

## Aging Definition

For each currently open incident:

aging = CURRENT_TIMESTAMP() - opened_date

Average aging is the average of the eligible incident ages.

## Time Filter

Time is OPTIONAL.

If the user supplies month and year:

Use opened_date to determine the month.

If no month is supplied:

Use ALL available history.

Do not ask for a month.

If the month is supplied without a year:

Ask for the year.

## Assignment Group

Assignment group is OPTIONAL.

If a specific assignment group is supplied:

Calculate average aging for that group.

If no group is supplied:

Calculate overall average aging across all groups.

Do not invent assignment groups.

## Overall Aging

Use the overall aging capability when the user asks:

- What is the average aging?
- What is the average age of open incidents?
- What is the average aging of open incidents?
- What is the average aging for August 2026?
- What is the average aging for Network Support?

## Aging By Assignment Group

Use the grouped capability when the user asks:

- What is the average aging for each assignment group?
- Show aging by assignment group.
- Compare average aging across assignment groups.
- Give me average open incident aging associated with each group.

## Examples

"What is the average aging of open incidents?"

Means:

- status in New, In Progress, On Hold
- all available history
- all assignment groups

"What is the average aging for August 2026?"

Means:

- currently open statuses
- opened_date in August 2026
- all groups

"What is the average aging for August 2026 for Network Support?"

Means:

- currently open statuses
- opened_date in August 2026
- assignment_group = Network Support

"What is the average aging for each assignment group?"

Means:

- currently open statuses
- all available history
- group by assignment_group

## Output

Return the metric.

Do not return individual incident records for an average-aging
question.

Return:

- period
- assignment group if applicable
- number of open incidents used
- average aging in days

Do not invent values.