# TripSure — three-minute demo

## Opening (20 seconds)
“An itinerary is easy to generate. Keeping it practical when budgets and conditions change is harder. TripSure pairs Azure language understanding with checks you can inspect.”

## Understand and plan (40 seconds)
Select Azure AI if configured. Enter: “Plan a 5-day trip from Delhi for 2 people under ₹50k, focused on nature and food, with a relaxed itinerary.” Click Understand request, review the fields, then Build my itinerary.

If Azure is unavailable, explicitly say: “This run uses our labelled offline fallback; the Azure adapter is implemented but not connected in this demonstration.” Do not imply the fallback is an LLM.

Point to estimated total **₹29,480**, contingency, two activity windows and reserved travel days. Say: “These are transparent planning estimates, not live bookable offers.”

## Adapt (45 seconds)
Open Adapt my trip. Lower the budget to **₹18,000**. Lock one low-cost riverside activity. Click Repair my itinerary. Point to cheaper accommodation and the before/after activity changes. The locked activity keeps its day/time.

Then simulate rain on an interior day. If a locked outdoor activity conflicts, show the explicit conflict, unlock it, and replan. Explain why silently dropping a user requirement would be wrong.

## Security (35 seconds)
Open Security lab and inspect the provided attack. Explain: “External source text never enters our model instructions or planner. It cannot change the budget or call a tool. This regex signal is illustrative; the isolation boundary is the actual protection.”

## Evidence and tests (30 seconds)
Open Sources & checks. Show what was checked and what remains unverified. Fetch live weather if internet permits, pointing out dates and retrieval timestamp. Show `python -m unittest discover -s tests -v` results.

## Close (10 seconds)
“TripSure makes its assumptions visible, preserves what the traveller values, and explains the trade-offs when a trip changes.”

## Three-person split
1. Azure setup and live connection check.
2. GitHub submission and final test run.
3. Demo narration and backup offline rehearsal.

## Before submitting
- Start the app successfully.
- Test one actual Azure extraction with the deployed model.
- Never commit the API key; confirm `.env` is ignored.
- Push main and open the GitHub URL to verify the files are present.
- Demonstrate the cheaper budget at ₹18,000; ₹35,000 is above the baseline so it may not require changes.
