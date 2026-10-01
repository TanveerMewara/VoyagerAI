# Voyager AI
A fast travel-planning application using Gemini 2.5 Flash and live OpenWeather observations.

## Interfaces
- Vercel web/API: FastAPI entry point in api/index.py; browser interface in web/. Plan, budget analytics, destination map, workflow, follow-up chat and PDF export.
- Local Streamlit: app.py keeps the existing dashboard experience.
- The active supervisor uses one Gemini call for itinerary, budget, hotels and tips. Weather runs concurrently and is appended as a current observation.
- graph.py and the three specialist-agent modules are an alternate, currently inactive LangGraph workflow. RAG/ChromaDB are not implemented in the active request path.

## Verified latency
Measured on 1 October 2026 using the same three sequential live cases (Paris, Tokyo, Goa):
- Mean first text: 17.81 seconds before optimization, 1.53 seconds after.
- Mean complete generation including weather: 29.76 seconds before, 4.07 seconds after.
- 3/3 plans completed, all requested days and sections appeared, and 3/3 PDFs exported.
- The optimization also shortened the default reports. These are small-sample local API measurements, not production SLAs, browser-load measurements or factual-accuracy scores.
- Raw data: data/evaluation/metrics.json and data/evaluation/fast/metrics.json.
- Analysis: data/evaluation/evaluation.md and data/evaluation/fast/comparison.md.
- A later real local FastAPI request took 19.90 seconds to first text and 22.35 seconds to completion, with a successful PDF export. It ran while the portfolio was compiling; it is not a controlled comparison or a Vercel measurement. See data/evaluation/web/live-api.json. Provider/host conditions can produce much slower requests than the earlier sample.

The modern Google GenAI client disables thinking for this routine planning task, streams output, reuses the client, and retries HTTP 503 up to twice before any text is emitted (0.5 and 1 second delays). Other errors are not blindly retried. Interrupted streams are not restarted.

## Local setup
Python 3.11+ is used locally. The Vercel runtime chooses its supported Python version.

1. Install: pip install -r requirements.txt
2. Set GOOGLE_API_KEY and WEATHER_API_KEY using .env.example as the variable-name reference.
3. Run the web version: python -m uvicorn api.index:app --host 127.0.0.1 --port 8502
4. Open http://127.0.0.1:8502

For Streamlit install requirements-streamlit.txt, then run streamlit run app.py.

## Vercel
Vercel detects the FastAPI entry point in api/index.py and handles application routes natively. vercel.json sets the function duration and excludes local environments, credentials, evaluation artifacts and archives from the function bundle. Do not add a catch-all rewrite to /api/index; it changes the path seen by FastAPI and breaks its routes.
1. Authenticate with vercel login.
2. Link this repository to a Vercel project (framework: FastAPI, project root: repository root).
3. Configure GOOGLE_API_KEY and WEATHER_API_KEY as server-side environment variables. Never put them in web/ or GitHub.
4. Deploy with vercel --prod. Check /api/health and generate a real plan before claiming the release is functional.

Deployment check on 1 October 2026: https://voyager-ai-theta.vercel.app serves the homepage, JavaScript, health endpoint, Paris map lookup and PDF export successfully. Desktop/mobile interface smoke checks passed using fixture model responses. Production AI generation and weather remain unverified until the server-side keys are configured; these checks are not production model-latency measurements. The health endpoint confirms application availability, not provider authentication.

The web version streams newline-delimited JSON events. The browser renders sanitized Markdown, keeps the last successful plan if regeneration fails, and fetches the PDF on demand rather than rebuilding it during chat. Secrets stay server-side.

## Tests and repeatable evaluation
- python -m unittest discover -s tests -v
- python -m tools.evaluate (up to three live, potentially billable model calls; writes evaluation artifacts)
- The 12 core regression checks cover response assembly, no-text failures, thinking/output settings, temporary and persistent 503s, interrupted streams, authentication errors, concurrent weather and long-trip configuration.
- Tests using mocked APIs establish behavior, not provider availability or real travel-data accuracy.

## Important limitations
- Prices, hotels and attraction advice are model estimates and can be outdated. Verify before booking.
- The first content audit found outdated museum and rail advice; the source reports remain as evidence.
- Current weather is not a multi-day forecast; there are no trip-date inputs.
- Family/Friends are traveler types, not actual headcounts; assumptions are labeled.
- The web map supports six known location aliases and clearly reports unavailable coordinates; it does not silently substitute another destination.
- Budget analytics on the web parses the generated budget table. The legacy Streamlit chart is a heuristic percentage allocation of the input budget, not a model-derived spending audit.
- Browser state is per page session. There is no database-backed conversation history, user authentication, booking integration or distributed rate limiter.
- The workflow graphic shows the actual conceptual request flow; it does not prove independent agent execution.
- Production cold starts, CDN availability, concurrency, provider quotas and the Vercel runtime may change observed performance.

## Explain this project
CHATGPT_PROJECT_PROMPT.md is a self-contained prompt and technical dossier for explaining the implementation, its history, tradeoffs, metrics and every source module without inventing capabilities.
