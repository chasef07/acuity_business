---
name: gtm-weekly
description: "Prepare the weekly GTM meeting: read the Sales CRM, Linear Sales tickets, and GTM playbook, interview Kyle, build the Acuity GTM weekly deck, and post it to #gtm. Use when asked to prep GTM weekly, the sales meeting, or the GTM deck."
---

# GTM Weekly

Turn the CRM, Linear, and Kyle's week into one deck that shows deals and work
moving, with an owner and date on every next step.

## Use when

- Preparing the weekly GTM meeting or its deck.
- Kyle asks where deals, channels, or GTM tickets stand this week.

## Not for

- One deal's meeting prep. Write that in the deal's Sales ticket.

## Sources

- Sales CRM: Google Sheet `Acuity Health Sales CRM V1` (`1A7BWSyREaq-xa06kYZDqem-cFAi22GW4yV8HOES3qqg`).
  Read `Dashboard` for the numbers, `Accounts` for deals, `Thesis Tests` for
  SAL-48, and `Ryan` for SAL-59. Run the `crm` skill first so they are current.
- Linear: the `Sales` team (key `SAL`).
- Playbook: Drive folder `Enterprise GTM Playbook` (`1f30WrQ4Vq97ZKyihg-zwH4GWVuoDj0jR`):
  offer, buyer and ICP, sales journey.
- Last week's deck: the latest deck post in Slack `#gtm` (`C0C0XSATN7Q`).

## Steps

1. **Read.** Pull open Sales tickets plus any updated in the last 7 days, the
   CRM rows, the playbook docs, and last week's `#gtm` post.
   Done when: you have each active deal's stage and next step, each open
   ticket's status and due date, and last week's decisions.

2. **Pre-read.** Show Kyle, briefly: next steps past due, deals with no next
   step, tickets overdue or without an owner, last week's decisions and whether
   each happened, and anything in Linear or email the CRM is missing.
   Done when: Kyle has seen the list.

3. **Interview.** Ask Kyle at most five questions at once: what changed on each
   active deal, new inbound, warm intros made this week, numbers for the
   tracking table, and what needs deciding. Use his facts as he states them; do
   not add dates or outcomes he did not give.
   Done when: every deal row has where it stands, next step, owner, and date
   from a source or from Kyle; anything else is `UNKNOWN`.

4. **Tickets.** Create the Sales tickets Kyle names, in the `Sales` team,
   assigned to Kyle unless he says otherwise, using Outcome & audience,
   Deliverable & work, Done when, and Sources. GTM work, including demos and
   MVPs for selling, belongs in Sales, not Product (Kyle, 2026-10-08).
   Done when: every new piece of work on the slides has a ticket ID.

5. **Build.** Copy `references/deck-example.json` to the scratchpad, fill it
   with this week's data, and run:

   ```bash
   npm install --prefix <scratchpad> pptxgenjs@4.0.1
   NODE_PATH=<scratchpad>/node_modules node ~/acuity_business/skills/gtm-weekly/scripts/build_deck.js <scratchpad>/deck.json <scratchpad>/gtm-weekly-YYYY-MM-DD.pptx
   ~/acuity_business/skills/gtm-weekly/scripts/render_slides.py <scratchpad>/gtm-weekly-YYYY-MM-DD.pptx <scratchpad>/render
   ```

   The builder exits 1 when a slide has too many rows. Look at every rendered
   slide; fix overflow or crowding by cutting words, not by shrinking type.
   Done when: the builder and renderer exit 0 and every slide reads cleanly.

6. **Review.** Send Kyle the deck and apply his edits in `deck.json`, then
   rebuild and re-render the slides you changed.
   Done when: Kyle approves the deck.

7. **Post** to `#gtm` after Kyle approves: upload the `.pptx` with the summary
   below as its comment.
   Done when: the Slack file link is in the reply.

8. **After the meeting,** update the CRM's next steps and the Linear tickets
   from the decisions Kyle reports, and record each change.
   Done when: every decision has an owner and date in the CRM or Linear.

## Deck

Slides, in order: cover, where we stand, active deals, this week and next
(Linear), inbound outside the ICP, channels, tracking, demo, decisions. Drop
an optional slide (inbound, tracking, demo) when it has nothing new.

- Light paper background on every slide; black boxes for callouts and ticket
  labels. Logo on the cover. Kyle did not want a full black slide.
- Every channel and initiative shows its ticket and status, so the slide shows
  work moving, not intentions.
- Deals inside the ICP and inbound outside it get separate slides.
- Numbers come from the CRM or Kyle. Show `—` until a number is counted.

## Output

```markdown
GTM Weekly deck for <date>: deals, this week and next, channels, and decisions.

Key items:
• <account>: <next step>, <date>
• Target: <weekly target> (<ticket>)
• <new initiative> (<ticket>)
```

## Guardrails

- Read the CRM and Drive; change them only in step 8, after the meeting.
- Post to Slack only after Kyle approves the deck and the message.
- Keep patient data out of the deck and the post.
