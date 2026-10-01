# VoyagerAI evaluation
Evaluated 1 October 2026, 18:14 IST. Three sequential live requests using configured Gemini and OpenWeather APIs. This is a smoke sample, not a load test.

## Measured performance
- Successful plans: 3/3 (100% of this sample).
- Mean time to first nonempty streamed text: 17.8105 seconds from supervisor start, including weather.
- Mean generation time: 29.7612 seconds, excluding PDF and UI rendering.
- Generation range: 25.8791 to 34.2174 seconds.
- Mean weather duration: 5.2656 seconds; live weather available in 3/3 requests.
- Required section coverage: 15/15 section checks. Requested day coverage: 3/3 plans.
- PDF generation: 3/3 successful; 0.5155 to 1.2479 seconds.
- Provider-reported total tokens: 14,557 across three requests. No monetary-cost estimate.
- Local deterministic streaming/weather checks: 6/6 passed using mocked APIs.
- Local 10-run microbenchmarks: fixture PDF mean 31.847 ms; map-object construction mean 23.492 ms. Neither measures browser rendering.

## Per-request results
Paris, 3 days: first text 16.6073 s; generation 29.1872 s; weather 6.4283 s; PDF 1.1904 s; 4,179 total tokens.
Tokyo, 5 days: first text 20.3227 s; generation 34.2174 s; weather 4.9818 s; PDF 1.2479 s; 5,919 total tokens.
Goa, 2 days: first text 16.5016 s; generation 25.8791 s; weather 4.3868 s; PDF 0.5155 s; 4,459 total tokens.

## Content findings
1. Paris recommends visiting the main Centre Pompidou building, although it is closed for renovation until 2030. Official source: https://www.centrepompidou.fr/en/centre-pompidou-is-transforming-itself/renovation-project-centre-pompidou-2030
2. Paris quotes Louvre admission at EUR 17; official general admission is EUR 22-32 depending on eligibility. Official source: https://www.louvre.fr/en/visit/hours-admission/tickets-and-prices
3. Tokyo's Nozomi/Japan Rail Pass advice omits the special additional ticket that allows pass holders to use these services. Official source: https://japanrailpass.net/en/use/special-ticket/
4. Paris budgets three hotel nights for arrival on day 1 and departure on day 3; Goa budgets two nights for departure on day 2. These exceed the itineraries' overnight stays unless an extra night is intended.
5. Goa assumes two friends, although the input says only "Friends". The app collects traveler type rather than an actual headcount.
6. Tokyo and Goa category totals add correctly (JPY 250,000 and INR 30,000). Paris base categories total EUR 910, with a separately stated EUR 590 contingency. Paris's presentation mixes a spending estimate and an allocation; this is not a clean comparable arithmetic pass/fail.
7. Current weather is used to advise on a multi-day trip, without travel dates or a multi-day forecast. Complete sections do not establish future weather accuracy.
8. The active app uses one Gemini request, despite its five-agent dashboard. The separate LangGraph pipeline is not the path called by app.py.
9. Map lookup supports six location keys and silently defaults unknown destinations to India; these benchmarks do not establish location accuracy.

## Interpretation
Streaming improves visible progress after the first chunk, but the measured initial wait is still 16.50-20.32 seconds. Weather precedes Gemini and contributes 4.39-6.43 seconds. The model/network portion remains the largest measured component. The removed 2.5-second UI delay is a code-derived saving; no historical live baseline was measured.

Three requests cannot establish production success rate, p95/p99, throughput, scalability or an overall factual-accuracy percentage. Hotel prices/availability and all itinerary facts have not been exhaustively verified. No overall quality score is assigned.

## Repeat
From C:\VoyagerAI run: venv\Scripts\python.exe -m tools.evaluate
This makes up to three live, potentially billable model requests. It overwrites data/evaluation/metrics.json and the three sample report files. local-metrics.json contains the separate deterministic measurements.

