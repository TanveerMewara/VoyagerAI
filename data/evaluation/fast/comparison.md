# Latency improvement verification

Measured 1 October 2026 on the same three live cases: Paris (3 days), Tokyo (5 days), Goa (2 days).

- Mean time to first text: 17.8105 seconds before, 1.5326 seconds after.
- Mean complete generation including weather: 29.7612 seconds before, 4.0682 seconds after.
- All three requests completed, covered every requested day and all five report sections, and exported to PDF.
- Seven focused regression tests passed, including proving that first text does not wait for weather.
- Streamlit generation, report ordering, follow-up chat and PDF reuse passed with mocked responses.

Changes: modern Google GenAI SDK, thinking budget set to zero, weather fetched concurrently, shorter plan/follow-up prompts, completed details rendered before charts and maps.

Tradeoff: default reports are concise (303-398 words here, compared with 1176-1676 previously). Ask follow-up questions for more detail. Current weather is appended separately and is not a forecast. This is a small sequential sample, not a production guarantee or a controlled model-quality comparison. API/network timing will vary.

Earlier measurements: ../metrics.json. Updated measurements: metrics.json. Both baselines have been preserved.
