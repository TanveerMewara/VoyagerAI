# Prompt: Explain Voyager AI From Start To Finish

Use everything below as the prompt. It is self-contained for the documented implementation. For literal line-by-line coverage, also attach the current source files and knowledge.md, excluding .env, credentials and bulky local environments. Documentation prepared 5 October 2026; saved measurements were taken 1 October 2026, not remeasured today.

---

You are a senior Python, AI and web engineer, a patient teacher and a demanding technical interviewer. Explain my project Voyager AI completely, from the problem and development evolution through architecture, code, testing, metrics, deployment and maintenance. Teach me enough to understand, demonstrate and defend it, not merely repeat its feature names.

Use the verified dossier below. Distinguish active implementation, inactive/legacy code, recorded measurements, code-derived expectations, limitations and future suggestions. Never invent code, missing features, author motivations, benchmark results or travel facts. If a detail is unavailable, say "Not established by the supplied implementation." If current source is attached, prioritize it and flag differences from this dated dossier. Do not claim you inspected linked repositories or tested deployed sites unless you actually did so. Never request or disclose API keys.

## Required Explanation Structure

1. Start with the project name, purpose, target users, solved problem, example trip request and actual generated output. Give a beginner introduction, a 60-second pitch and a technical interview summary.
2. Explain the supported development history: original Streamlit/alternate graph, latency work, feature preservation, lean web/API adaptation, evaluation, Vercel routing/key fixes, real production smoke and portfolio link. Do not invent a full original design diary or unsupported dates.
3. List the stack by layer, why each library is used and alternatives/tradeoffs. Separate Voyager AI's Python/browser stack from the separate Next.js portfolio. Explain that unpinned Python requirements are not a lockfile.
4. Draw the real architecture and separate web, local Streamlit and inactive LangGraph paths. Explain precisely which services run concurrently and which steps wait. Do not portray conceptual agent labels as execution traces.
5. Trace a request end to end: browser input -> HTTP JSON -> Pydantic validation -> worker/queue -> supervisor -> Gemini/weather -> callbacks -> NDJSON -> DOM -> successful state -> analytics/map/chat/export. Include exact relevant fields and limits.
6. Explain every module below and every function/class named. For attached source, explain imports, arguments, return values, local variables, control flow, error branches and important lines, including helper/event-handler functions. Without source, do not fabricate unseen lines or exact CSS/HTML values.
7. Teach the concepts used: ASGI versus a development server, typed validation, threads/executors, queues/events/locks, synchronous generators, caching/TTL/client reuse, context managers, iterators/callbacks, cumulative streaming, TextDecoder/partial line buffers, DOM events, Markdown sanitization, XML escaping, BytesIO, state lifetimes and monotonic timing.
8. Explain prompts and model settings: four generated sections plus appended weather, day coverage, hotel-night count, group-size assumptions, output token budget, thinking budget, follow-up context and why shorter responses trade detail for speed.
9. Explain every UI feature and differences between interfaces: report, workflow, timing, budget/chart, known-location map, chat, PDF, summaries/sidebar, busy/error/empty states and preservation after failures.
10. Explain missing key, empty text, temporary/persistent 503, partial-stream interruption, other provider errors, timeouts, weather fallback, invalid input, disconnect, unsupported map, unparseable budget and PDF limitations. Cover bounded retries without understating network delays.
11. Explain all saved metrics using units, formulas, sample sizes and source files. Include the slower later local case and real production case, not only favorable results. Explain client-versus-server timing, token fields, format-versus-factual quality, changed output lengths and unmeasured metrics.
12. Explain tests and what they do NOT prove. Separate offline mocked tests, browser fixtures/map tiles, live API samples and production smoke. Do not claim new test execution from historical records.
13. Explain setup, configuration, deployment, GitHub/portfolio integration and the routing/key issues. Show safe commands with placeholders only. Explain redeployment after hosting environment changes and why health is not provider readiness.
14. Explain security/privacy and remaining risks: input limits, server-only keys, sanitized rendering, PDF escaping, external providers/CDNs, no login/database/distributed limiter and public API cost/abuse. Do not infer provider retention or security certification.
15. Explain limitations and prioritized improvements, explicitly labeled future. No active RAG, ChromaDB, autonomous memory, verified bookings or five-agent execution claims.
16. Give a reproducible demo checklist, debugging decision tree and interview Q&A, including difficult questions about architecture honesty, small samples, hallucinations, caches, retry idempotence and deployment cold starts.
17. Finish with a glossary, a concise architecture recap and a source-coverage checklist showing every supplied module discussed. State unresolved details instead of guessing.

For long explanations, complete coherent sections and indicate exactly where to continue. Keep facts, interpretations and proposals distinguishable. Explain the small details instead of claiming completeness with a superficial overview.

## Verified Project Dossier

### Identity And Scope

Voyager AI is Tanveer Mewara's travel-planning project. Repository https://github.com/TanveerMewara/VoyagerAI; recorded deployed app https://voyager-ai-theta.vercel.app; portfolio entry https://tanveer-portfolio-coral.vercel.app/projects/voyager-ai. It collects destination, days, budget, traveler type, interests and departure, generating itinerary, estimated expenses, hotels, tips and current weather with maps, analytics, follow-up questions and PDF download. It does not make actual bookings or establish travel-fact correctness.

The current supervisor makes ONE combined Gemini model request while a weather task runs concurrently. There is also an inactive sequential LangGraph implementation. UI labels and conceptual diagrams do not make the active app a five-agent orchestration system. There is no active RAG/ChromaDB retrieval.

### Active Planning And Model Code

`agents/supervisor_agent.py`: supervisor_agent(destination, days, budget, travelers, interests, departure, on_chunk=None). Its prompt requests Itinerary, Budget Breakdown, Hotel Recommendations and Travel Tips in Markdown. Requested days include morning/afternoon/evening. Expense categories include return travel, hotel, food, local transport, activities, contingency and total; three hotels and five short tips are requested. It asks for max(0, days-1) hotel nights, labeled unknown Family/Friends headcounts and estimated rather than guaranteed prices. It does not give the model current weather or allow invented readings.

ThreadPoolExecutor(max_workers=1) submits get_weather before model generation. ask_gemini streams concurrently; final assembly gets the weather future, appends # Weather with actual observation/fallback and current-not-forecast wording, calls the callback with the completed report and returns it. The executor joins. Weather failure preserves model output. Token allowance is min(8192, max(2048, 1024+days*180)); 30 days gives 6424.

`utils/gemini.py`: google.genai, not deprecated google.generativeai; load_dotenv; MODEL_NAME="gemini-2.5-flash". get_client() uses lru_cache(maxsize=1), requires GOOGLE_API_KEY and constructs genai.Client with HTTP timeout 60000 ms and HttpRetryOptions(attempts=1). This is process-local client reuse.

ask_gemini(prompt, on_chunk=None, max_output_tokens=8192) sets ThinkingConfig(thinking_budget=0) and an output allowance. Without callback it uses generate_content and response.text; with callback it uses generate_content_stream, skips textless chunks, joins text parts and passes cumulative text. Empty output raises RuntimeError.

Application retries only APIError code 503, at most three total attempts. Waits are 0.5 then 1 second. No partial-output request is restarted: interruption produces a friendly error; persistent 503 produces a temporarily-busy message; other API errors propagate. Total request delays include network timeout, not just retry sleep.

ask_followup(previous_plan, user_question, on_chunk=None) sends saved plan plus latest question, asks for a concise direct answer without repeating the plan and uncertainty about prices/availability; max_output_tokens=2048. Displayed earlier messages are not sent as conversational context.

### Weather

`tools/weather.py`: get_weather(city) normalizes whitespace/case, reads WEATHER_API_KEY and skips network if absent. _get_weather(city, api_key) uses cachetools.cached with TTLCache(maxsize=128, ttl=600) and RLock. Cache is per process, includes credential in its key, can cache fallback failures and does not coordinate quotas across instances.

requests.get calls OpenWeather /data/2.5/weather with q/appid/units=metric and timeout=(3.05,5) seconds. Extracted fields: temperature, condition, humidity, wind speed. Non-200/exception paths yield fallback text. This is current observation, not trip-date forecast.

### API And Streaming

`api/index.py` exports FastAPI app, serves web/index.html at GET /, mounts web/ at /static and provides:

- GET /api/health: status ok and model name; no upstream authentication test.
- GET /api/location: Tokyo/Japan/Paris/Dubai/Goa/London coordinates or null; no arbitrary geocoding or silent fallback.
- POST /api/plan: TripRequest destination 1-120 characters/non-whitespace; days 1-30; budget <=120; travelers Solo/Couple/Family/Friends; interests <=1500; departure <=120.
- POST /api/chat: ChatRequest plan 1-60000 and question 1-2000/non-whitespace.
- POST /api/pdf: PdfRequest plan 1-60000; escaped text -> BytesIO PDF -> application/pdf download.

stream_request(operation) uses a worker thread, queue, cancelled Event and perf_counter. Events are text(cumulative), working(heartbeat after five seconds waiting), done(final text, generation_seconds, first_text_seconds) or error. NDJSON is newline-delimited JSON, not SSE. Cache-Control:no-store. RuntimeError messages are shown; unexpected details are hidden. Disconnect signals cancellation; the callback checks it, but blocked provider calls are not instantly terminated. Server first-text measures callback time, not browser paint; generation includes planning/weather, not later PDF or rendering.

### Browser And Streamlit Interfaces

`web/index.html`: trip form, visible conceptual workflow, Plan/Budget/Map/Chat tabs, PDF/status/timing controls. `web/style.css`: responsive compact layout, constrained map/chart sizes. `web/app.js`: selector/render, activate, showError, stream, budgetAnalytics, destinationMap, message and form/chat/download handlers. fetch streams JSON; TextDecoder and a retained line buffer handle fragmented NDJSON. marked output is sanitized with DOMPurify. Model HTML is not inserted unsanitized.

savedPlan is browser memory; successful regeneration clears displayed chat; failed regeneration restores the last successful plan/features. Plan/chat share busy guard. PDF is fetched on demand. No persistent browser/database conversations. Budget analytics extracts numeric rows from a generated two-column budget table, skips headers/totals and creates Chart.js chart/table without arithmetic validation or invented fallback. Leaflet uses OpenStreetMap tiles/attribution and known markers, resizes on tab activation, shows unavailable message for unknown destinations.

Browser libraries are pinned CDN marked, DOMPurify, Chart.js, Leaflet and lucide with an external Paris photo. Exact versions/URLs require current web/index.html. CDN and tile availability are external dependencies.

`app.py`: original Streamlit form/session_state travel_plan, trip_details, chat_history, execution_time, cached PDF bytes. Five artificial 0.5-second sleeps were removed; output streams into a placeholder. Successful plans alone replace saved state; chat/PDF resets after success. Report is shown before secondary components, split on level-one headings rather than mandatory horizontal separators.

It retains Budget Analytics, Multi-Agent Workflow, AI Execution Summary, Trip Summary, Destination Map, PDF Download, recommendation factors, chatbot, sidebar/footer. Agent presentation labels are conceptual. st_folium(returned_objects=[]) reduces interaction reruns; cached PDF reused, on_click="ignore" on download. Failed regeneration stores generation_error and st.rerun() shows previous report/features; initial failure without saved plan stops. Local session is not durable storage.

### Other Modules And Configuration

- `agents/planner_agent.py`: planner_agent(destination, days, interests), alternate itinerary model prompt.
- `agents/budget_agent.py`: budget_agent(destination, days, budget, travelers), alternate expense model prompt.
- `agents/hotel_agent.py`: hotel_agent(destination, budget, travelers), alternate five-hotel prompt.
- `graph.py`: TravelState TypedDict; planner_node, budget_node, hotel_node, weather_node, report_node; StateGraph planner -> budget -> hotel -> weather -> report -> END -> compiled travel_graph. Inactive in both UIs; three sequential model calls, not parallel specialists.
- `utils/report_generator.py`: generate_report(itinerary, budget, hotels, weather); alternate formatted report, misleading forecast wording for current observations.
- `tools/map.py`: create_map(destination), Folium known aliases, legacy unknown-destination India fallback (web API deliberately differs).
- `utils/budget_chart.py`: create_budget_chart(total_budget), strips rupee/format characters, integer parsing or 50000 fallback, Plotly allocation 40% hotel/25% food/15% transport/20% activities. Heuristic, not verified accounting.
- `utils/workflow.py`: create_workflow(), conceptual Graphviz User/Supervisor/Planner/Budget/Hotel/Weather/Output nodes.
- `tools/pdf_generator.py`: generate_pdf(content, filename="VoyagerAI_TravelPlan.pdf"), ReportLab SimpleDocTemplate/Paragraph, newlines -> breaks, filename or file-like output; web escapes first; not full Markdown rendering.
- `tools/evaluate.py`: evaluate(output_directory="data/evaluation"), sequential three live scenarios, provider usage_metadata, weather/first-text/generation timing, heading/Day N checks, PDF attempts, JSON/Markdown output. Format regexes are not a semantic quality judge; live calls can be billed and chosen artifacts overwritten.
- `ui/dashboard.py`, `ui/sidebar.py`, `ui/styles.py`, package __init__.py files and `assets/style.css`: empty scaffolding at inspected snapshot.
- `tests/test_latency.py`, `tests/test_web_api.py`, `scripts/web-smoke.mjs`: regression and browser checks described below.
- `data/evaluation/`: preserved reports, audit and raw metrics; fast/ optimized run, web/ local/production evidence/screenshots.
- `requirements.txt`: fastapi, uvicorn, google-genai, python-dotenv, requests, reportlab, cachetools. `requirements-streamlit.txt`: includes base plus streamlit, streamlit-folium, folium, plotly, graphviz, pandas, langchain, langgraph, langchain-google-genai. Python packages are not version locked.
- `vercel.json`: detected FastAPI api/index.py, maxDuration300, excluded local environments/.env/tests/data/vector_db/archive/tools; no catch-all rewrite. `.vercelignore` excludes secret/bulky uploads; `.gitignore` ignores actual environment values/local artifacts; `.env.example` is placeholders only.
- `README.md`: interfaces/setup/limits; `CHATGPT_PROJECT_PROMPT.md`: earlier dossier; `knowledge.md`: exhaustive saved metric reference; `prompt.md`: this prompt.

### Metrics And Evidence

Recorded 1 October 2026. Original/optimized runs each attempted/planned/succeeded 3/3/3, with sample success 100%; all three had weather, requested-day markers, five headings/100% format coverage and PDFs. Format coverage is not factual accuracy. Times below are seconds. Each list names first text, generation, weather, PDF, total tokens and words.

Original `data/evaluation/metrics.json`:
- Paris3d: 16.6073, 29.1872, 6.4283, 1.1904, 4179 tokens, 1333 words.
- Tokyo5d: 20.3227, 34.2174, 4.9818, 1.2479, 5919 tokens, 1676 words.
- Goa2d: 16.5016, 25.8791, 4.3868, 0.5155, 4459 tokens, 1176 words.
- Mean first text17.8105; generation29.7612.

Optimized `data/evaluation/fast/metrics.json`:
- Paris3d: 2.3980, 3.7465, 2.7206, 0.1298, 755 tokens, 306 words.
- Tokyo5d: 1.1193, 4.7187, 4.7052, 0.1413, 956 tokens, 398 words.
- Goa2d: 1.0805, 3.7393, 3.1521, 0.1191, 743 tokens, 303 words.
- Mean first text1.5326; generation4.0682.

Additional original per-case fields (Paris/Tokyo/Goa): characters8647/11128/7556; stream_updates49/61/43; PDF bytes8570/10505/7645; prompt tokens216/220/217; candidates2331/2926/2051. Optimized: characters2065/2819/2015; updates13/17/13; PDF bytes3708/3993/3594; prompt tokens251/254/251; candidates504/702/492. Original total tokens do not equal prompt+candidates; separate reasoning tokens were not saved, so do not assert a measured reasoning breakdown.

Mean=sum(values)/count; reduction=(old-new)/old*100; speedup=old/new. Reports shrank from1176-1676 to303-398 words, provider/network/cache conditions changed and generation excludes UI/PDF. These are observational samples, not an isolated performance experiment. Raw artifacts retain their earlier "No measured before/after baseline" caveat; explain its evaluation-stage context without rewriting evidence.

`data/evaluation/local-metrics.json`: six deterministic mocked checks passed (stream assembly, synchronous text, normalized cached weather, connect/read timeout, timeout fallback, missing-key no-network). Ten-run PDF fixture mean31.847ms/median26.691ms/max76.267ms; map construction mean23.492ms/median19.348ms/max55.153ms. These exclude real planning, browser map rendering and tile networking. Removed2.5-second display wait is code-derived, not separately measured total speedup.

`data/evaluation/web/live-api.json`: one real local FastAPI request during simultaneous portfolio compilation, firsttext19.902s, generation22.349s, 314words, PDFsuccess=true, done event/message=null. Retain this slower case; not production or a controlled regression.

`data/evaluation/web/production-smoke.json`: sample1 on recorded production origin; Paris2d/EUR1000/Solo/Museums and parks/departureLondon. PlanHTTP200; client firsttext4.212s/completion6.387s; server firsttext0.588s/generation2.577s; 262words; current weather present; PDFHTTP200/valid signature; follow-up chat completed. Client includes request/network overhead, server timings differ; cold start unestablished; facts/prices unverified.

No p95/p99, throughput/load limit, long-term production success rate, numerical factual accuracy, monetary model cost or cold-start distribution was measured. Do not turn a three-case 100% format/sample-success result into a quality or reliability claim. Current pricing would be required to estimate money from usage.

### Test Coverage

Historical20 passing unit tests:12core+8API. Core covers skipped empty streamed chunks/assembly/thinking0, synchronous text, pre-output503recovery, bounded persistent503, no restart after partial text, no authentication-error retries, empty-output rejection, follow-up plan/2048limit, text before weather completion, weather failure preserving plan and30day/nights configuration.

API tests cover home/static/health, streamed completion/timings, validation before model invocation, hidden unexpected exception details, friendly busy message, saved-plan chat, in-memory escaped PDF and unknown-map null. Most provider paths are mocked.

Browser smoke checks at1440x1000 and390x844 cover tabs, budget rows/chart, loaded real map tiles, chat, failed-regeneration report/controls preservation, no horizontal overflow and no page errors. Planning/chat are fixture responses; this is not a live provider test. Separate saved production case verifies one actual provider plan/chat/weather/PDF path. Do not claim tests were rerun on documentation day.

### History, Deployment And Operational Details

The supported history is: existing Streamlit/alternate graph -> sleep/stream/state/PDF improvements -> modern SDK/zero thinking/concise combined prompt/concurrent weather/bounded503 handling -> preserved feature/failure behavior -> lean FastAPI/browser implementation -> local/browser tests with honest slow-run evidence -> Vercel authentication and native routing -> approved server-side key configuration/redeploy -> successful production smoke -> portfolio live link/GitHub documentation -> these two documentation files. Exact original author decisions beyond evidence are unknown.

A redundant rewrite to /api/index originally caused live homepage/API404s after native FastAPI detection; removing it fixed routes. Missing GOOGLE_API_KEY produced "Set GOOGLE_API_KEY before generating a travel plan." Existing local GOOGLE_API_KEY/WEATHER_API_KEY were uploaded only after explicit approval as server-side production secrets, followed by redeployment and real verification. Keys must never enter frontend/GitHub. Original GitHub auto-deploy connection initially required an additional account connection; direct CLI deploy succeeded. Do not claim automatic integration was enabled without evidence.

Local setup: install requirements.txt; configure .env using example names; python -m uvicorn api.index:app --host127.0.0.1 --port8502 (show correctly spaced executable commands in your explanation). For original UI install requirements-streamlit.txt and streamlit run app.py. Offline tests: python -m unittest discover -s tests -v. Live evaluation: python -m tools.evaluate, warn about costs/overwriting. Local Python documented3.11+; recorded Vercel build3.12. Vercel login/link root as FastAPI/set production keys/deploy --prod; changing environment requires redeploy. Health checks alone do not test model availability.

### Honest Limitations And Security

Historical audit found closed Pompidou-building advice, outdated Louvre price, incomplete Japan Rail Pass/Nozomi advice, extra hotel nights and assumed group size. Preserved reports/audit are evidence, not current travel-policy assertions. Prompt fixes request verification/assumptions/correct nights, not guaranteed accuracy. No numerical truth score is established.

Weather is current, maps alias-limited, budget arithmetic unvalidated, Streamlit chart heuristic, chat stateless across reloads, PDFs basic. No booking API, real dates/headcounts, login, durable database, distributed limiter, active retrieval or active multi-specialist orchestration. External provider/CDN/tile/network/cold-start/quota conditions vary. Server-side secrets/sanitization/input bounds/PDF escaping address particular risks but not all security concerns. User trip/plan data goes to model provider; destination goes to weather provider; provider retention is not established. Public unauthenticated requests can incur costs.

Future-only suggestions: dates/headcounts, verified travel data, arithmetic/factual validation, broader geocoding/forecasting, durable private chat, abuse controls, production load/cold-start studies, richer PDF formatting, retrieval/true orchestration if justified.

Conclude with a candid assessment that I can explain in an interview without exaggerating. Any claim beyond this dossier must be grounded in supplied current source or explicitly identified as unestablished.
