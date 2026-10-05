# Voyager AI Knowledge Reference

Documentation prepared: 5 October 2026. Source and saved evidence were inspected locally; measurements below were recorded on 1 October 2026, not rerun for this documentation task. Deployment links describe the recorded deployment, not a fresh availability check.

## Project Basics

Voyager AI is Tanveer Mewara's personalized travel-planning application. It accepts destination, trip duration, budget, traveler type, interests and departure city. It produces a daily itinerary, estimated budget, hotel suggestions, travel tips and current weather. Users can inspect budget analytics and maps, ask follow-up questions and export a PDF.

- Repository: https://github.com/TanveerMewara/VoyagerAI
- Published application: https://voyager-ai-theta.vercel.app
- Portfolio project: https://tanveer-portfolio-coral.vercel.app/projects/voyager-ai
- Main web interface: FastAPI plus HTML/CSS/JavaScript.
- Optional original interface: local Streamlit dashboard.
- Active planning implementation: one combined Gemini request plus concurrent weather, not five independent model agents.
- Outputs are planning suggestions, not verified bookings, guaranteed prices or authoritative travel advice.

## Architecture And Request Flow

```text
Browser trip form
  -> POST /api/plan -> Pydantic TripRequest validation
  -> stream_request: worker thread + queue + cancellation event
  -> supervisor_agent
       -> weather executor -> get_weather -> cached OpenWeather request
       -> ask_gemini -> reusable Google GenAI client -> Gemini text stream
  -> cumulative text callback -> queue -> NDJSON -> browser Markdown rendering
  -> append current weather -> final done event + server timings
  -> savedPlan -> budget chart / destination map / chat / PDF

Local Streamlit form -> same supervisor and Gemini/weather helpers
  -> streamed placeholder -> successful plan saved in session_state
  -> local Plotly / Folium / Graphviz / PDF / follow-up chat
```

Weather is submitted before model generation starts. The first model text does not wait for weather. The final report waits for the weather future and includes its result or fallback. The executor joins before returning; weather concurrency does not eliminate weather's contribution to completion time.

The browser uses fetch and a streaming response reader. Each NDJSON line is a JSON event, not a Server-Sent Events frame. `text` contains the entire accumulated report so far, `working` is a heartbeat, `done` contains final text and timings, and `error` contains a message. The browser replaces the preview with cumulative text rather than appending each snapshot and duplicating earlier content.

Chat sends the saved plan and latest question to Gemini. Earlier displayed chat turns are not model context. PDF generation is a separate request made on demand. Maps use known coordinates rather than an external geocoding service.

## Technology Stack

### Web Runtime

- Python: planning, API, weather, evaluation and PDF code.
- FastAPI: HTTP routes, validated request models, streaming/file responses.
- Uvicorn: local ASGI application server.
- Pydantic: used by FastAPI for request constraints; a transitive dependency rather than an explicit requirements.txt entry.
- google-genai: modern Google GenAI client and streaming Gemini calls.
- python-dotenv: local environment configuration.
- requests: OpenWeather HTTP requests with connect/read timeouts.
- cachetools: bounded weather TTL cache.
- ReportLab: in-memory PDF creation.
- Standard library: threads, executor, Queue, Event, RLock, lru_cache, BytesIO, pathlib, json, perf_counter and XML escaping.

The lean `requirements.txt` lists fastapi, uvicorn, google-genai, python-dotenv, requests, reportlab and cachetools without pinned versions. Do not treat a locally installed SDK version as a reproducible dependency lock.

### Browser Dependencies

HTML, CSS and plain JavaScript; marked for Markdown; DOMPurify for sanitization; Chart.js for a doughnut chart; Leaflet with OpenStreetMap tiles/attribution; lucide icons; an external Paris photograph. These are public CDN/media dependencies, not bundled offline assets. Versions are pinned in web/index.html; inspect that file for exact URLs.

### Optional Local And Alternate Code

`requirements-streamlit.txt` includes the base requirements plus streamlit, streamlit-folium, folium, plotly, graphviz, pandas, langchain, langgraph and langchain-google-genai. These packages are not proof that all corresponding capabilities are active. LangGraph is used by the inactive alternate graph; there is no active RAG or ChromaDB retrieval.

Vercel hosts the Python web application. Git/GitHub store source. The separate portfolio uses Next.js, React and TypeScript; those are not Voyager AI's application framework.

## Module And File Guide

- `api/index.py`: FastAPI app; TripRequest, ChatRequest, PdfRequest; home, health, location, plan, chat and pdf endpoints; stream_request bridges synchronous planning to streamed HTTP using a worker and queue. Web PDF text is escaped first.
- `agents/supervisor_agent.py`: supervisor_agent(destination, days, budget, travelers, interests, departure, on_chunk=None); creates the combined planning prompt, submits weather concurrently, streams model output, appends actual weather and returns the report.
- `utils/gemini.py`: MODEL_NAME, get_client(), ask_gemini() and ask_followup(); client reuse, thinking/output configuration, synchronous/streaming support, empty-response checks and bounded 503 retries.
- `tools/weather.py`: get_weather(city) normalizes the destination and skips networking when the key is absent; _get_weather(city, api_key) implements cached current observations and fallback messages.
- `web/index.html`: trip inputs, conceptual workflow, Plan/Budget/Map/Chat tabs, status/timing elements and PDF command; CDN assets, no API keys.
- `web/style.css`: responsive layout, compact controls, fixed-format map/chart areas and visual states.
- `web/app.js`: selector/render helpers, activate(), showError(), stream(), budgetAnalytics(), destinationMap(), message(), form submission/chat/export event handlers; in-memory savedPlan, busy guard, chart/map/marker state and fragmented NDJSON parsing.
- `app.py`: original Streamlit dashboard; session state, streamed generation, report sections, sidebar, summaries, maps, charts, workflow, cached PDF and chat. It uses the active supervisor, not travel_graph.
- `tools/pdf_generator.py`: generate_pdf(content, filename="VoyagerAI_TravelPlan.pdf"); ReportLab SimpleDocTemplate and Paragraph, newline-to-break conversion; accepts a path or file-like output. It is not a full Markdown-to-PDF renderer.
- `tools/map.py`: create_map(destination) builds a Folium map for six aliases; unknown locations have a legacy India fallback, unlike the web API's explicit unavailable result.
- `utils/budget_chart.py`: create_budget_chart(total_budget) parses an integer after removing rupee/format characters, falls back to 50000 when parsing fails, and allocates 40% hotel, 25% food, 15% transport and 20% activities in Plotly. This is a heuristic, not extracted expenses.
- `utils/workflow.py`: create_workflow() returns a conceptual Graphviz User/Supervisor/Planner/Budget/Hotel/Weather/Output diagram. Labels are not runtime evidence of independent agent calls.
- `agents/planner_agent.py`: planner_agent(destination, days, interests), standalone itinerary prompt; inactive in the main path.
- `agents/budget_agent.py`: budget_agent(destination, days, budget, travelers), standalone expense prompt; inactive in the main path.
- `agents/hotel_agent.py`: hotel_agent(destination, budget, travelers), standalone five-hotel prompt; the active combined supervisor requests three hotels.
- `graph.py`: TravelState TypedDict, planner_node, budget_node, hotel_node, weather_node, report_node and compiled travel_graph. The alternate sequence is planner -> budget -> hotel -> weather -> report -> END, with three sequential model calls. Neither current UI invokes it.
- `utils/report_generator.py`: generate_report(itinerary, budget, hotels, weather), formats the alternate report. Its forecast wording is misleading for a current-weather tool.
- `tools/evaluate.py`: evaluate(output_directory="data/evaluation"), runs three live scenarios sequentially; captures usage/timing/format/PDF evidence and writes JSON/reports. It can incur API cost and overwrite selected output artifacts.
- `tests/test_latency.py`: 12 core regression tests for model and supervisor behavior.
- `tests/test_web_api.py`: 8 API behavior tests, mostly with mocked planning/model operations.
- `scripts/web-smoke.mjs`: Playwright desktop/mobile workflow checks using fixture planning/chat responses and actual browser assets/map tiles.
- `data/evaluation/`: original reports, raw metrics, audit and deterministic checks; `fast/` contains the optimized three-case run; `web/` contains local/production smoke evidence and screenshots.
- `requirements.txt`, `requirements-streamlit.txt`: web versus optional local/alternate dependencies.
- `vercel.json`: api/index.py function maxDuration=300 seconds and excluded local/secret/bulky files; native detected FastAPI routing, no catch-all rewrite.
- `.vercelignore`: deployment-upload exclusions; `.gitignore`: secrets, virtual environments, generated/cache/bulky files; `.env.example`: variable names/placeholders only.
- `README.md`: setup and limitations; `CHATGPT_PROJECT_PROMPT.md`: earlier explanation dossier; `knowledge.md`: this reference; `prompt.md`: requested complete explanation prompt.
- `ui/dashboard.py`, `ui/sidebar.py`, `ui/styles.py`, package __init__.py files and `assets/style.css`: empty scaffolding at the inspected snapshot, not hidden implementations.

## Model And Prompt Details

Model: `gemini-2.5-flash`. Client creation is lazy and memoized with lru_cache(maxsize=1). GOOGLE_API_KEY is required. SDK HTTP timeout is 60000 ms; HttpRetryOptions(attempts=1) disables SDK-level repeated attempts. GenerateContentConfig sets ThinkingConfig(thinking_budget=0).

ask_gemini(prompt, on_chunk=None, max_output_tokens=8192) supports both non-streamed response.text and streamed generation. It ignores chunks without text, assembles fragments, calls the callback with cumulative text and rejects an empty response. No exact output length or quality is guaranteed by a token ceiling.

The supervisor requests four Markdown sections: Itinerary, Budget Breakdown, Hotel Recommendations, Travel Tips. Each requested day includes morning/afternoon/evening; budget includes return travel, hotel, food, local transport, activities, contingency and total; three hotels and five short tips are requested. It asks for max(0, days-1) hotel nights, labeled unknown group-size assumptions, estimates rather than guaranteed prices and no fabricated weather readings. Actual weather is the fifth section appended by Python.

Planning output allowance: min(8192, max(2048, 1024 + days*180)); 30 days yields 6424 tokens. Follow-up output allowance: 2048 tokens. Chat asks for a concise direct answer grounded in the saved plan, without repeating it, with uncertainty about live prices/availability.

503 handling: at most three total application attempts, with 0.5 seconds then 1 second between attempts. Restart is allowed only before any text has reached the user. A partial interrupted stream is not silently replayed. Persistent overload yields a friendly temporary-busy error. Other API errors are not blindly retried. Retry sleeps total at most 1.5 seconds, but request timeouts make the total worst-case delay longer.

## API Contracts And State

- GET `/`: web/index.html.
- GET `/api/health`: status/model only; not provider authentication or readiness.
- GET `/api/location?destination=Paris`: known coordinates or null. Aliases: Tokyo, Japan, Paris, Dubai, Goa, London.
- POST `/api/plan`: destination 1-120 characters and non-whitespace; days 1-30; budget at most 120; travelers Solo/Couple/Family/Friends; interests at most 1500; departure at most 120. Returns streamed NDJSON.
- POST `/api/chat`: plan 1-60000 characters; non-whitespace question 1-2000; streamed NDJSON.
- POST `/api/pdf`: plan 1-60000 characters; application/pdf with download filename.

stream_request uses perf_counter, a worker thread, queue and cancellation Event. `working` events are emitted after five seconds waiting for a queue item. Done reports first_text_seconds and generation_seconds; first text is measured at the server callback, not browser paint. Cache-Control is no-store. Expected RuntimeError messages are returned; unexpected exceptions become a generic error. Disconnect signals cancellation, but an upstream blocked network call is not immediately terminated. There is no distributed concurrency guard or rate limiter.

Browser savedPlan and displayed chat exist only in page memory. A failed regeneration preserves the successful plan, analytics/export/chat access; a successful replacement clears displayed chat. Markdown is parsed then sanitized. Budget parsing uses the generated two-column numeric table and skips total/header rows; it neither validates arithmetic nor invents a fallback budget when parsing fails. Leaflet resizes after the map tab opens and explicitly reports unsupported coordinates.

Streamlit uses travel_plan, trip_details, chat_history, execution_time and cached PDF bytes in session_state. It streams a preview, splits report sections on level-one headings, reuses PDF bytes and uses st_folium(returned_objects=[]) to reduce interaction reruns. Download uses on_click="ignore". Failed regeneration saves generation_error and reruns to show the previous plan; an initial failure without a saved plan stops. Session state is not a durable database.

## Weather Configuration

WEATHER_API_KEY is the OpenWeather credential. Destinations are normalized for cache reuse. TTLCache(maxsize=128, ttl=600) with RLock is process-local, not shared across Vercel instances. The key includes the city and API key. Locking protects cache access, not service-wide quotas; fallback failures may also be cached.

OpenWeather `/data/2.5/weather` uses q, appid and units=metric with requests timeout=(3.05, 5) seconds. Results contain temperature, humidity, condition and wind speed. Missing key avoids the network; non-200 responses/timeouts/errors yield fallback text. This is current weather, not a forecast for a future trip.

## Recorded Metrics

All measurements below are historical evidence, not promises about current performance. Original and optimized live samples each contain three sequential cases, with no load/concurrency test. Times are seconds unless marked otherwise. A sample success percentage is not a production success-rate estimate.

### Original Live Sample

Source: `data/evaluation/metrics.json`, timestamp 2026-10-01T18:14:56.204603+05:30.

- Attempted/planned/successful: 3/3/3; recorded sample success: 100%; mean first text: 17.8105; mean complete generation: 29.7612.
- Paris, 3 days: first text 16.6073; generation 29.1872; weather 6.4283; PDF 1.1904; 8647 characters; 1333 words; 49 stream updates; PDF 8570 bytes; prompt tokens 216; candidate tokens 2331; total tokens 4179.
- Tokyo, 5 days: first text 20.3227; generation 34.2174; weather 4.9818; PDF 1.2479; 11128 characters; 1676 words; 61 stream updates; PDF 10505 bytes; prompt tokens 220; candidate tokens 2926; total tokens 5919.
- Goa, 2 days: first text 16.5016; generation 25.8791; weather 4.3868; PDF 0.5155; 7556 characters; 1176 words; 43 stream updates; PDF 7645 bytes; prompt tokens 217; candidate tokens 2051; total tokens 4459.
- Each case: successful=true, weather_available=true, pdf_success=true, requested_days_present=true; all five section_checks=true and section_coverage_percent=100.

### Optimized Live Sample

Source: `data/evaluation/fast/metrics.json`, timestamp 2026-10-01T18:25:04.922817+05:30.

- Attempted/planned/successful: 3/3/3; recorded sample success: 100%; mean first text: 1.5326; mean complete generation: 4.0682.
- Paris, 3 days: first text 2.3980; generation 3.7465; weather 2.7206; PDF 0.1298; 2065 characters; 306 words; 13 stream updates; PDF 3708 bytes; prompt tokens 251; candidate tokens 504; total tokens 755.
- Tokyo, 5 days: first text 1.1193; generation 4.7187; weather 4.7052; PDF 0.1413; 2819 characters; 398 words; 17 stream updates; PDF 3993 bytes; prompt tokens 254; candidate tokens 702; total tokens 956.
- Goa, 2 days: first text 1.0805; generation 3.7393; weather 3.1521; PDF 0.1191; 2015 characters; 303 words; 13 stream updates; PDF 3594 bytes; prompt tokens 251; candidate tokens 492; total tokens 743.
- Each case: successful=true, weather_available=true, pdf_success=true, requested_days_present=true; all five section_checks=true and section_coverage_percent=100.

Mean = sum of measured case values / number of measured cases. Relative reduction = (original mean - optimized mean) / original mean * 100. Speedup = original mean / optimized mean. These compare observed samples, not an isolated causal experiment: report lengths and provider/network conditions changed. Original total tokens exceed prompt+candidate counts; do not assume the difference is measured reasoning tokens because no separate reasoning count was saved.

### Deterministic Checks And Microbenchmarks

Source: `data/evaluation/local-metrics.json`; mocked APIs, fixture PDF, not live outputs.

- Checks passed: 6/6. Streaming assembly/updates, non-streamed text, normalized weather-cache reuse, connect/read timeouts, timeout fallback and missing-key no-network behavior all true.
- PDF fixture: 10 runs; mean 31.847 ms; median 26.691 ms; maximum 76.267 ms.
- Map object construction: 10 runs; mean 23.492 ms; median 19.348 ms; maximum 55.153 ms.
- Removed display delay: 2.5 seconds, derived from removing five 0.5-second sleeps; not a separately measured end-to-end speedup.
- PDF/map microbenchmarks do not include live report generation, browser rendering, network tile loading or production cold starts.

### Later Local FastAPI Case

Source: `data/evaluation/web/live-api.json`; one real local request during a concurrent portfolio build.

- Event type done; server first text 19.902 seconds; generation 22.349 seconds; report 314 words; pdf_success=true; message=null.
- This slower result is retained to show variability. It is neither a controlled regression comparison nor a Vercel result.

### Production Smoke Case

Source: `data/evaluation/web/production-smoke.json`; 1 October 2026; sample_count=1; origin https://voyager-ai-theta.vercel.app.

- Request: Paris, 2 days, EUR 1000, Solo, Museums and parks, departing London.
- Plan HTTP 200; client first text 4.212 seconds; client completion 6.387 seconds.
- Server first text 0.588 seconds; server generation 2.577 seconds; report 262 words.
- Current weather observation present=true; PDF HTTP 200; PDF signature valid=true; followup_chat_completed=true.
- Client times include request/network overhead and are not interchangeable with server callback timings. Cold-start status was not established. Travel facts/prices were not independently verified.

### Test And Browser Evidence

Historical completed checks: 20 unit tests passed (12 core and 8 API), plus desktop 1440x1000/mobile 390x844 browser workflows. Browser checks cover tabs, budget rows/chart, actual loaded map tiles, chat, failed-regeneration preservation, no horizontal overflow and no page errors. AI/chat responses in browser smoke tests are fixtures, not provider availability tests. Separate live production smoke evidence verifies one actual plan/chat/PDF path.

No measured p95/p99, throughput, sustained production reliability, factual-accuracy score, model monetary cost, cold-start distribution or comprehensive security score is available. Format/day coverage is not correctness. Tokens are provider-reported when available; cost requires a separate current pricing calculation. No new tests or API calls were run to create these documents.

## Evaluation Limitations And Quality Findings

The first content audit identified stale museum/rail advice, including recommending the closed Centre Pompidou building, outdated Louvre admission information, incomplete Japan Rail Pass/Nozomi advice, excess hotel-night budgets and assumed friend headcounts. These are historical audit findings, not assertions about today's travel policies. See `data/evaluation/evaluation.md` and preserved reports. Prompt improvements request verification, correct night counts and labeled assumptions but do not prove hallucinations are eliminated.

Both saved metrics JSON files retain the older limitation text "No measured before/after baseline" from their original evaluation stage. The later two-sample comparison uses those preserved runs as an observational before/after comparison; it is still not a controlled benchmark of equivalent outputs. Do not silently rewrite the original artifacts.

Hotel existence, attraction opening times, prices, budget arithmetic, recommendation relevance and safety need independent checking. Weather freshness can differ due to caching. There are no actual booking APIs, real traveler headcount/date inputs, arbitrary geocoding, durable conversation store, user authentication, distributed rate limiting, active RAG/ChromaDB or active specialist-agent orchestration.

## Development And Optimization History

This is the supported implementation history, not a complete reconstruction of the author's original decisions:

1. An original Streamlit experience and alternate specialist-agent graph existed. Dashboard labels and diagrams described agents, but the currently active supervisor path uses one combined model call.
2. Artificial display sleeps were removed; first output was streamed; report visibility, PDF reuse and map rerun behavior were improved.
3. The modern GenAI SDK, zero thinking, concise prompts, client reuse, concurrent weather and bounded overload retries were applied; original and optimized three-case results were saved.
4. Failed regeneration was fixed to preserve the previous successful report/features rather than hiding them.
5. A lean FastAPI/browser interface was added for Vercel while preserving optional Streamlit; Markdown sanitization, validated inputs and escaped in-memory PDF text were included.
6. Local/API/browser verification and the slower local case were recorded honestly.
7. Vercel sign-in and native FastAPI deployment succeeded. A redundant catch-all rewrite initially caused homepage/API 404s and was removed. Server-side keys required explicit approval and redeployment; without GOOGLE_API_KEY the app reported "Set GOOGLE_API_KEY before generating a travel plan."
8. A real production plan/weather/PDF/chat check passed. The portfolio source and deployment were updated with the live link. The detailed explanation dossier and metric evidence were committed to GitHub.
9. These requested knowledge.md and prompt.md documents were added on 5 October 2026. They do not change runtime behavior.

## Setup, Deployment And Troubleshooting

```powershell
pip install -r requirements.txt
# Configure local .env using .env.example names; never commit actual values.
python -m uvicorn api.index:app --host 127.0.0.1 --port 8502
# Optional original dashboard:
pip install -r requirements-streamlit.txt
streamlit run app.py
# Offline behavior tests:
python -m unittest discover -s tests -v
# Live evaluation: billable provider calls; may overwrite artifacts.
python -m tools.evaluate
```

For Vercel: authenticate; link the repository root as FastAPI; set GOOGLE_API_KEY and WEATHER_API_KEY as production server-side environment variables; redeploy after changes; check `/`, `/api/health`, a real streamed plan, weather, chat and PDF. maxDuration=300 is configuration, not a latency promise. Native FastAPI routing needs no rewrite to /api/index. Local Python is documented as 3.11+; the recorded deployment used Python 3.12. Dependencies are not locked, so reproduce/version-pin before claiming deterministic installs.

Missing Google key: configure the correct environment and redeploy/restart. 503: bounded retry applies before output; persistent errors require waiting/retrying, not infinite loops. Other quota/authentication errors require checking provider credentials/limits; they are not automatically retried. Weather fallback: check key, destination, timeout and cache. Unknown map: supported aliases only. Missing budget chart: inspect generated table/currency formatting; no fabricated fallback. Invalid request: inspect Pydantic validation and input bounds. Stream failure: inspect network/provider/server logs without printing credentials. PDF success means a valid file was generated, not perfect Markdown formatting.

Secrets stay in local ignored .env or server-side hosting configuration. The browser sends trip information and plan context to the backend; Gemini receives prompt/context and OpenWeather receives destination. No durable application database is implemented; no guarantee about third-party provider retention is established here. DOMPurify and escaping address particular rendering risks, not all security threats. A public endpoint can incur provider cost; authentication, rate limits and abuse controls remain important improvements.

## Future Work

Add actual dates/headcounts, sourced travel data, factual and budget-arithmetic validation, broader geocoding, forecasts, durable chat with appropriate privacy controls, public-demo abuse protection, production load/cold-start measurements and richer PDFs. Introduce genuine multi-agent orchestration or retrieval only when implemented, measured and justified. Suggested work must not be presented as current functionality.

## How To Use The Explanation Prompt

`prompt.md` is self-contained for a broad detailed explanation. For an exact line-by-line explanation, attach current source files and this reference as well; no static dossier can supply every unseen line or future change. Actual attached source takes precedence over dated documentation. Never attach .env or credential files.
