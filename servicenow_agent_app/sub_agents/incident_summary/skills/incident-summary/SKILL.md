---
name: incident-summary
description: Analyze overall incident counts and assignment-group summaries.
---

# Incident Summary Skill

## Purpose

Provide high-level counts and summaries of incidents.

## Total Incident Count

When the user asks:

- total incidents
- count of incidents
- number of incidents in the table
- how many incidents are there
- total records

count ALL records in the incidents table.

Do not require a month.

Do not require an assignment group.

Do not filter status unless the user explicitly requests a status.

Example:

"What is the count of incidents in the table?"

Means:

ALL incidents
ALL dates
ALL assignment groups
ALL statuses

## Currently Open Incidents

Currently open incidents have status:

- New
- In Progress
- On Hold

Closed incidents have:

- Closed

When the user asks for open incident counts without a date
or assignment-group filter, use ALL available history.

## Assignment Group Breakdown

When the user asks:

- open incidents by assignment group
- open incidents associated with each assignment group
- open incident count for each group
- how many open incidents does each group have

return one count for each assignment group.

Do not return individual incident records unless the user
explicitly asks for details.

## Time Filter

Time is OPTIONAL.

If the user specifies a month, apply the month.

If the user does not specify a month, use all available data.

Do not ask for a month unless the user explicitly requires
a monthly analysis.

## Assignment Group

Assignment group is OPTIONAL.

If the user asks for all groups, provide the grouped result.

If a specific assignment group is provided, restrict the result
to that group.

Do not invent assignment groups.

## Output

For count questions, return counts only.

Do not return incident records.

Only return incident records when the user explicitly asks
for details, records, tickets, or incident IDs.