---
name: crm
description: "Keep the Acuity Sales CRM current: log outreach and meetings from Gmail into Activity, propose stage and next-step changes for Kyle to approve, and report what is overdue or stale. Use when asked to update, sync, clean, or review the CRM, or before GTM weekly."
---

# CRM

Turn what happened in email and in Kyle's week into dated Activity rows, so the
Dashboard counts emails, meetings, and days to book without anyone typing them.

## Use when

- Syncing the CRM with recent email, or backfilling a lead's history.
- Kyle reports calls, LinkedIn messages, intros, or meetings to log.
- Before `gtm-weekly`, so the deck reads current numbers.

## Not for

- Building the GTM deck. Use `gtm-weekly`.
- Research on new prospects. That goes on the `Boost Patients Prospects` tab.

## The sheet

Google Sheet `Acuity Health Sales CRM V1`
(`1A7BWSyREaq-xa06kYZDqem-cFAi22GW4yV8HOES3qqg`).

| Tab | Write? | Contract |
|---|---|---|
| `Accounts` | A:V | One row per active Kyle or Chase account. `Account` (A) is the key every other tab joins on; never rename one without updating its Activity rows. W:AC are header formulas; never write there. |
| `Ryan` | Rows 8+, A:V | Ryan's accounts, same columns as Accounts starting at row 7. Rows 1–5 are his summary; F5 is Kyle's review-date input. |
| `Inactive` | A:V | Same columns as Accounts. Accounts Kyle has parked or ruled out. |
| `Activity` | Append only | `Date`, `Account` (exact name from Accounts, Ryan, or Inactive), `Type` (from `Lists!C`), `Summary`, `Link` (Gmail thread), `Logged by`. Never edit or delete a row Kyle wrote. |
| `Thesis Tests` | C:K | One row per SAL-48 thesis call. B is a formula. |
| `Dashboard` | D6 and F6 only, when Kyle gives them | Formulas over Accounts and Activity, plus inputs: default AI $/hr (D6) and workdays per month (F6). |
| `Lists` | Only when Kyle adds a value | Dropdown values for stage, source, activity type, owner. |
| `CRM V1 archive` | Never | Pre-October 2026 tab, kept until Kyle deletes it. |

`Pipeline value` (E) holds a per-row formula: average calls per day (F) ×
average minutes per call (G) ÷ 60 × AI $/hr (H, or the Dashboard default
when blank) × workdays per month × 12.
Kyle types over it when he has a real number (shown in blue); never overwrite a
typed value. On a new row, copy E's formula from the row above. Write a typed
number only from a proposal or Kyle.

Log only 1:1 contact. Skip webinar invites, reminders, recordings, and other
group or broadcast emails: first touch is the first 1:1 email, call, form, or
intro (Kyle, 2026-10-09).

`Meeting booked` is the activity type that drives days to book. Log it on the
day the meeting was agreed, not the day it happens; log `Meeting held` on the
day it happens.

## Steps

1. **Read.** Read `Accounts!A:AC`, `Ryan!A7:AC`, `Activity!A:F`, and `Inactive!A:A`.
   Done when: you have every account name, its email domain from `Email` (O),
   and the latest Activity date per account.

2. **Gather.** Search Gmail from the day after the latest `Logged by` agent row
   (or the range Kyle names) for threads with each account's contact email or
   domain. Ask Kyle, at most five questions at once, for what email can't show:
   calls, texts, LinkedIn messages, warm intros, and meetings agreed in person.
   Done when: each candidate event has a date, an account, a type, and a source
   (thread link or "Kyle").

3. **Log.** Append one Activity row per event with `Logged by` set to
   `crm agent` or `Kyle`. Skip an event already logged with the same date,
   account, and type. A thread with several messages is one row per message
   that changed something (sent, replied, booked), not one per email.
   Done when: the appended rows read back with dates shown as dates.

4. **Propose.** List the Accounts changes the evidence supports: stage, next
   step, next step due, source, contact fields, and accounts to move to
   Inactive. Give each its evidence. Apply only what Kyle approves. To move an
   account between Accounts, Ryan, and Inactive, copy its A:V values to the
   target tab (keep E's formula unless it was typed), then delete the source row.
   Done when: every approved change is written and every rejected one is
   dropped.

5. **Report.** Read the Dashboard and send Kyle the output below.
   Done when: Kyle has the report.

## Output

```markdown
CRM synced through <date>: <n> activities logged, <n> account changes applied.

Needs attention:
• Overdue: <account> — <next step> (due <date>)
• No next step: <account>
• No touch in 14+ days: <account> (<days>)

This week: <emails sent> emails, <meetings booked> meetings booked, <warm intros> of <target> warm intros.
```

## Guardrails

- Every Activity date comes from an email timestamp or from Kyle. Never infer a
  date from the order of notes; write `UNKNOWN` in Summary and ask.
- Change Accounts stage, owner, or Inactive status only with Kyle's approval.
- No patient names, dates of birth, or clinical details in any cell.
- Do not send email or messages to prospects. This skill reads and records.
