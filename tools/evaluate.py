"""Run a small live evaluation: python -m tools.evaluate."""
import json
import re
import statistics
import time
from datetime import datetime
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from agents import supervisor_agent as supervisor
from tools.pdf_generator import generate_pdf
from utils import gemini

CASES = [
    ("Paris", 3, "EUR 1500", "Solo", "Art, food, museums", "London"),
    ("Tokyo", 5, "JPY 250000", "Couple", "Food, culture, parks", "Osaka"),
    ("Goa", 2, "INR 30000", "Friends", "Beaches, local food", "Mumbai"),
]
SECTIONS = ("itinerary", "budget breakdown", "hotel recommendations", "weather", "travel tips")


def evaluate(output_directory="data/evaluation"):
    results = []
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    for destination, days, budget, travelers, interests, departure in CASES:
        row = {"destination": destination, "requested_days": days}
        first_text = None
        chunks = 0
        usage = {}
        model_api = gemini.get_client().models
        original_generate = model_api.generate_content_stream
        original_weather = supervisor.get_weather

        def measured_generate(*args, **kwargs):
            response = original_generate(*args, **kwargs)
            for chunk in response:
                metadata = getattr(chunk, "usage_metadata", None)
                if metadata is not None:
                    for field in ("prompt_token_count", "candidates_token_count", "total_token_count"):
                        usage[field] = int(getattr(metadata, field, 0) or 0)
                yield chunk

        def measured_weather(city):
            started = time.perf_counter()
            text = original_weather(city)
            row["weather_seconds"] = round(time.perf_counter() - started, 4)
            row["weather_available"] = "Temperature" in text
            return text

        def update(text):
            nonlocal first_text, chunks
            if text.strip():
                if first_text is None:
                    first_text = time.perf_counter() - started
                chunks += 1

        started = time.perf_counter()
        try:
            with patch.object(model_api, "generate_content_stream", side_effect=measured_generate), patch.object(supervisor, "get_weather", side_effect=measured_weather):
                report = supervisor.supervisor_agent(destination, days, budget, travelers, interests, departure, on_chunk=update)
            row["success"] = bool(report.strip())
            headings = [re.sub(r"[^a-z ]", "", line.lower()).strip() for line in report.splitlines() if line.lstrip().startswith("#")]
            coverage = {section: any(section in heading for heading in headings) for section in SECTIONS}
            row["section_checks"] = coverage
            row["section_coverage_percent"] = round(100 * sum(coverage.values()) / len(SECTIONS), 1)
            day_numbers = {int(number) for number in re.findall(r"\bday\s*(\d+)\b", report, flags=re.I)}
            row["requested_days_present"] = set(range(1, days + 1)).issubset(day_numbers)
            row["characters"] = len(report)
            row["words"] = len(report.split())
            row["tokens"] = usage
            row["generation_seconds"] = round(time.perf_counter() - started, 4)
            pdf_started = time.perf_counter()
            try:
                buffer = BytesIO()
                generate_pdf(report, filename=buffer)
                row["pdf_success"] = buffer.getvalue().startswith(b"%PDF")
                row["pdf_bytes"] = len(buffer.getvalue())
            except Exception as error:
                row["pdf_success"] = False
                row["pdf_error_type"] = type(error).__name__
            row["pdf_seconds"] = round(time.perf_counter() - pdf_started, 4)
            (output / (destination.lower() + ".md")).write_text(report, encoding="utf-8")
        except Exception as error:
            row["success"] = False
            row["error_type"] = type(error).__name__
            row["generation_seconds"] = round(time.perf_counter() - started, 4)
        row["first_text_seconds"] = round(first_text, 4) if first_text is not None else None
        row["stream_updates"] = chunks
        results.append(row)
        print(json.dumps(row), flush=True)
        if row.get("error_type") in {"ResourceExhausted", "PermissionDenied", "Unauthenticated", "InvalidArgument", "NotFound"}:
            break

    successful = [row for row in results if row["success"]]
    summary = {
        "evaluated_at": datetime.now().astimezone().isoformat(),
        "mode": "live APIs; sequential smoke sample, not a load test",
        "attempted": len(results),
        "planned": len(CASES),
        "successful": len(successful),
        "success_rate_percent": round(100 * len(successful) / len(results), 1),
        "mean_generation_seconds": round(statistics.mean(row["generation_seconds"] for row in successful), 4) if successful else None,
        "mean_first_text_seconds": round(statistics.mean(row["first_text_seconds"] for row in successful if row["first_text_seconds"] is not None), 4) if any(row["first_text_seconds"] is not None for row in successful) else None,
        "results": results,
        "limitations": [
            "Small sample: no production reliability, throughput or p95/p99 claim.",
            "Section and day checks measure format coverage, not factual correctness.",
            "Hotel existence, prices, budget arithmetic, safety and recommendation relevance require independent validation.",
            "Compare saved runs with the same cases; API conditions and output detail may differ.",
            "Generation timings include weather and model calls but exclude UI rendering and PDF creation.",
            "Cached weather can make repeated runs faster; no per-request weather freshness claim.",
            "Token counts are provider-reported when available; monetary cost is not estimated."
        ]
    }
    (output / "metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("SUMMARY " + json.dumps(summary), flush=True)
    return summary


if __name__ == "__main__":
    evaluate()
