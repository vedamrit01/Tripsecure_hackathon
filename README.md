# 🧭 TripSure — Good trips have a plan B

An Azure-ready AI travel planning prototype for a hackathon. Natural-language intent becomes validated constraints; a deterministic planner builds a costed itinerary and repairs it around locked activities and simulated rain.

## Start in two minutes

Requires Python 3.10+ (tested with Python 3.12).

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://localhost:8501. Click **Build my itinerary** for the offline demo. No API key is needed for the offline deterministic planner. On Windows you can also double-click `START_WINDOWS.bat`.

## Connect your Azure resource

1. In Foundry, open **View deployments**. Deploy a chat-completions-compatible model that your resource permits, or use an existing deployment.
2. Copy the **deployment name** exactly. A model catalogue listing is not a deployment.
3. Copy `.env.example` to `.env`. Set the key, deployment name and Azure OpenAI endpoint. Alternatively enter them in the sidebar on your local machine.
4. Start/restart the app, select **Azure AI**, then click **Understand request**.
5. Review the extracted fields and click **Build my itinerary**. Extraction never silently commits a plan.

```dotenv
AZURE_OPENAI_ENDPOINT=https://ved.openai.azure.com/openai/v1/
AZURE_OPENAI_DEPLOYMENT=YOUR_EXACT_DEPLOYMENT_NAME
AZURE_OPENAI_API_KEY=YOUR_KEY
```

The endpoint above comes from the supplied resource screenshot; no resource was provisioned by this project. Do not use the `/api/projects/...` project endpoint. The REST adapter calls `/openai/v1/chat/completions`, supplies the deployment as `model`, and uses `api-key` authentication. A chat-completions-compatible deployment is required. Model access, quota and live connectivity must be verified in your own subscription.

HTTP 401: check key. 403: check permissions. 404: check deployment name/endpoint. 429: quota or rate limit. On failure the existing plan is preserved; fallback is selected explicitly, never presented as an Azure result.

Never commit `.env` or `.streamlit/secrets.toml`. Both are ignored, as are secret files in Docker builds. Do not paste the key in GitHub, screenshots, or the presentation. Running the app locally is the simplest hackathon setup. Public multi-user hosting needs authentication, per-user quota controls and production secret management; those are not implemented.

## What works

- Azure natural-language extraction into bounded, validated fields; offline regex fallback with an explicit mode label.
- Curated Delhi → Rishikesh / Jaipur planning, 3–7 days, 1–8 travellers.
- Deterministic cost arithmetic, double-occupancy room rounding and 10% contingency.
- Preference matching and comfort/value alternatives within the total budget.
- Reserved arrival/return days and two non-overlapping activity windows per sightseeing day.
- Locked activities preserve their original day and time. Accommodation **tier**, not an actual hotel, can be locked.
- Rain simulation replaces outdoor activities. A locked outdoor activity creates an explicit conflict.
- Side-by-side change messages, source links, validation results, tool trace and itinerary downloads.
- Optional real HTTP tools: official tourism page fetch and Open-Meteo seven-day forecast. Failures are shown; no fake live response.
- Security lab illustrating isolation of untrusted documents from the model and planner.

## Architecture

```text
User text → Azure extraction (or labelled regex fallback)
          → schema/constraint validation → user reviews fields
          → curated catalogue → deterministic candidate planner
          → integer cost calculator → feasibility checks → itinerary
Replan form + locks + simulated rain → same planner and validators
Official-page / weather adapters → evidence panel (never instructions)
```

`app.py`: UI and per-session state. `core.py`: constraints, solver, checks, diff. `catalog.py`: curated demo data. `services.py`: Azure and bounded network adapters. `tests/`: deterministic evaluation cases and UI smoke tests.

Azure handles language understanding; it does not invent prices, tool names, URLs, or executable code. Tool orchestration is application-controlled, not an autonomous multi-agent framework. The agent demonstrates intent → tools/data → planning → validation → replanning.

## Grounding and honest limits

Official tourism links support destination/attraction background only. Costs, travel durations, venue coordinates, workshop availability and proposed times are **illustrative estimates**, not sourced live offers. No route optimization, live hotel/flight search, bookings, verified opening hours, accessibility certification or named hotel inventory is implemented. A 10% buffer is not a price guarantee.

The official-page fetch shows retrieved text and timestamp but does not automatically verify itinerary claims. Weather is a real Open-Meteo forecast when the API is reachable; forecast dates must match the trip before use. Rain replanning is a separate, clearly labelled **simulation**, not an automated forecast decision. Both pace settings currently use a conservative two-activity cap. Adventure is an explicitly unfulfilled preference.

## Security model

- Only validated scalar/list constraint fields can emerge from model output; unknown fields and invalid ranges fail closed.
- User input and model output cannot choose outbound URLs, execute code or access a filesystem tool.
- Azure resource hosts are allowlisted, HTTPS is required, redirects disabled, and project/custom endpoints rejected.
- Tourism and weather URLs are fixed in code. Network calls have timeouts and response size limits.
- Untrusted source documents are displayed as text and never passed to the model or planner. Pattern detection is illustrative; isolation is the security boundary.
- No booking, payment, email or shell capability is offered to the model.
- Keys are used only in the Azure request header, not model messages or trip exports. Provider error bodies are not displayed. No prompts or keys are intentionally logged.
- Streamlit session state separates plans; no shared plan cache. This is not a production authentication boundary.
- No Azure Prompt Shields integration is claimed. No guarantee of complete prompt-injection detection is claimed.

## Tests and evaluations

```bash
python -m unittest discover -s tests -v
```

22 backend tests cover budget arithmetic, infeasible budgets, cheaper replanning, exact locks, rain conflicts, supported trip lengths, room counts, invalid inputs, SSRF endpoint checks, document isolation, response bounds and mocked Azure responses. Two Streamlit smoke tests exercise build/replan/security and parse/build flows when Streamlit is installed. GitHub Actions runs the full suite with dependencies installed. See `EVALUATION.md` for execution results and limits.

Tests evaluate this implementation; they are not a broad benchmark of model accuracy. Azure tests use mocked responses; live Azure verification remains a team setup step.

## GitHub submission

This download contains a local Git repository with the project committed. In the extracted `tripsure` folder:

```bash
git status
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Create an **empty repository** (do not initialize it with a README) first. Authenticate with your own GitHub account if prompted. If your extraction tool dropped `.git`, run:

```bash
git init -b main
git add .
git commit -m "Build TripSure adaptive travel agent"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

For subsequent changes, run `git add .`, `git commit -m "Describe change"`, then `git push`. Keep your key only in `.env`. Never force-push over teammates' work.

## Optional container run

```bash
docker build -t tripsure .
docker run --rm -p 8501:8501 --env-file .env tripsure
```

Docker configuration is provided; a container deployment was not performed. Local launch is sufficient to demonstrate the Azure-backed app.

## References

- Azure v1 API: https://learn.microsoft.com/en-us/azure/foundry/openai/api-version-lifecycle
- Rishikesh: https://www.uttarakhandtourism.gov.in/destination/rishikesh
- Jaipur: https://www.tourism.rajasthan.gov.in/jaipur.html
- Weather API and usage terms: https://open-meteo.com/en/docs

Weather data attribution: Open-Meteo. Review its service terms before commercial deployment.

## Travel companion upgrade

- Travel-inspired forest-green and warm-ivory interface with bundled destination photography, editorial typography and responsive layouts. Fonts fall back to installed fonts offline.
- **Compare escapes:** evaluate both destinations using the same confirmed constraints, then select a proposal. Choosing a destination resets old activity locks.
- **Calendar export:** download planned activities as `.ics` events for calendar import. India local times are converted to UTC; events are proposals, not bookings.
- **Travel kit:** destination-aware packing checklist with progress and a text download.
- **Group expenses:** record actual spending, choose who paid, undo the latest entry, calculate equal shares with exact whole-rupee settlements, and download the ledger as JSON. Estimates remain separate from actual spending.

Checklist and expense data are session-only. Changing destination, departure date or group size resets the travel kit; download your expense record first. No cloud persistence or payment execution is implied. Destination comparisons do not inherit locks from the active plan.

Photo source: [Yatra Rishikesh travel blog](https://www.yatrablog.com/10-things-that-you-didnt-know-about-rishikesh). Photograph bundled for the destination inspiration display; third-party image rights remain with their owner.

Validation: 29 automated tests, including three Streamlit interaction tests. New coverage checks India-time calendar export, expense conservation and settlement, invalid expenses, destination comparison, packing, and destination-switch state reset. Live Azure calls remain unverified.
