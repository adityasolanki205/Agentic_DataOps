---
name: opened-incidents
description: Analyze incidents based on opened_date with optional month, year, and assignment-group filters.
---

# Opened Incidents Skill

## Purpose

Analyze incidents using their `opened_date`.

## Definition

An "opened incident" is an incident whose `opened_date`
falls within the requested period.

This is different from a currently open incident.

## Time Filter

Time is OPTIONAL.

If the user specifies a month and year:

- Filter using opened_date.

If the user does not specify a month:

- Use ALL available history.

Never force the user to specify a month.

If the user provides a month without a year, ask for the year.

## Assignment Group

Assignment group is optional.

Valid groups:

- Application Dev
- Database Admin
- Service Desk
- Cloud Infrastructure
- Cyber Security
- Network Support

If supplied, filter by assignment group.

If not supplied, include all groups.

## Count Rule

Count is the DEFAULT.

If the user asks:

- total
- count
- number
- how many

use the count tool.

Do not return individual records.

## Detail Rule

Return records only when the user explicitly asks for:

- details
- records
- tickets
- incident IDs
- list of incidents 

## Monthly Filtering

For a specific month, filter using `opened_date`.

Example:

August 2026:

```text
opened_date >= 2026-08-01
AND
opened_date < 2026-09-01