import threading
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from agents import supervisor_agent as supervisor
from utils import gemini


class GeminiLatencyTests(unittest.TestCase):
    def setUp(self):
        self.api = Mock()
        self.client_patch = patch.object(
            gemini, "get_client", return_value=SimpleNamespace(models=self.api)
        )
        self.client_patch.start()
        self.addCleanup(self.client_patch.stop)

    def test_streaming_skips_empty_chunks_and_disables_thinking(self):
        self.api.generate_content_stream.return_value = iter([
            SimpleNamespace(text=None),
            SimpleNamespace(text="Hello "),
            SimpleNamespace(text="world")
        ])
        updates = []
        result = gemini.ask_gemini("test", on_chunk=updates.append)
        self.assertEqual(result, "Hello world")
        self.assertEqual(updates, ["Hello ", "Hello world"])
        config = self.api.generate_content_stream.call_args.kwargs["config"]
        self.assertEqual(config.thinking_config.thinking_budget, 0)

    def test_non_streaming_remains_supported(self):
        self.api.generate_content.return_value = SimpleNamespace(text="Complete")
        self.assertEqual(gemini.ask_gemini("test"), "Complete")

    def test_temporary_overload_recovers_without_initial_wait(self):
        self.api.generate_content.side_effect = [
            gemini.errors.APIError(503, {"error": {"message": "busy"}}),
            SimpleNamespace(text="Complete")
        ]
        with patch.object(gemini.time, "sleep") as sleep:
            self.assertEqual(gemini.ask_gemini("test"), "Complete")
        self.assertEqual(self.api.generate_content.call_count, 2)
        sleep.assert_called_once_with(0.5)

    def test_stream_overload_before_first_text_is_retried(self):
        def overloaded_stream():
            raise gemini.errors.APIError(503, {"error": {"message": "busy"}})
            yield

        self.api.generate_content_stream.side_effect = [
            overloaded_stream(), iter([SimpleNamespace(text="Recovered")])
        ]
        updates = []
        with patch.object(gemini.time, "sleep"):
            self.assertEqual(gemini.ask_gemini("test", on_chunk=updates.append), "Recovered")
        self.assertEqual(updates, ["Recovered"])

    def test_persistent_overload_has_bounded_retries_and_friendly_error(self):
        self.api.generate_content.side_effect = gemini.errors.APIError(
            503, {"error": {"message": "busy"}}
        )
        with patch.object(gemini.time, "sleep") as sleep:
            with self.assertRaisesRegex(RuntimeError, "temporarily busy"):
                gemini.ask_gemini("test")
        self.assertEqual(self.api.generate_content.call_count, 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [0.5, 1.0])

    def test_interrupted_stream_is_not_restarted(self):
        def interrupted_stream():
            yield SimpleNamespace(text="Partial")
            raise gemini.errors.APIError(503, {"error": {"message": "busy"}})

        self.api.generate_content_stream.return_value = interrupted_stream()
        updates = []
        with patch.object(gemini.time, "sleep") as sleep:
            with self.assertRaisesRegex(RuntimeError, "interrupted"):
                gemini.ask_gemini("test", on_chunk=updates.append)
        self.assertEqual(updates, ["Partial"])
        self.assertEqual(self.api.generate_content_stream.call_count, 1)
        sleep.assert_not_called()

    def test_authentication_errors_are_not_retried(self):
        error = gemini.errors.APIError(403, {"error": {"message": "forbidden"}})
        self.api.generate_content.side_effect = error
        with patch.object(gemini.time, "sleep") as sleep:
            with self.assertRaises(gemini.errors.APIError):
                gemini.ask_gemini("test")
        self.assertEqual(self.api.generate_content.call_count, 1)
        sleep.assert_not_called()

    def test_empty_response_is_not_saved_as_success(self):
        self.api.generate_content_stream.return_value = iter([
            SimpleNamespace(text=None)
        ])
        with self.assertRaisesRegex(RuntimeError, "no text"):
            gemini.ask_gemini("test", on_chunk=Mock())

    def test_followup_uses_existing_plan_with_smaller_output_limit(self):
        self.api.generate_content.return_value = SimpleNamespace(text="Use the metro")
        self.assertEqual(gemini.ask_followup("Paris plan", "Transport?"), "Use the metro")
        kwargs = self.api.generate_content.call_args.kwargs
        self.assertIn("Paris plan", kwargs["contents"])
        self.assertIn("Transport?", kwargs["contents"])
        self.assertEqual(kwargs["config"].max_output_tokens, 2048)


class SupervisorLatencyTests(unittest.TestCase):
    def test_first_text_does_not_wait_for_weather(self):
        weather_started = threading.Event()
        allow_weather = threading.Event()
        updates = []

        def weather(city):
            weather_started.set()
            if not allow_weather.wait(timeout=2):
                raise AssertionError("Model did not release weather")
            return "Temperature: 22 C"

        def generate(prompt, on_chunk=None, **kwargs):
            self.assertTrue(weather_started.wait(timeout=1))
            self.assertFalse(allow_weather.is_set())
            on_chunk("# Itinerary\nDay 1: Museum")
            allow_weather.set()
            return "# Itinerary\nDay 1: Museum"

        with patch.object(supervisor, "get_weather", side_effect=weather), patch.object(supervisor, "ask_gemini", side_effect=generate):
            report = supervisor.supervisor_agent(
                "Paris", 1, "EUR 500", "Solo", "Art", "London",
                on_chunk=updates.append
            )
        self.assertNotIn("Temperature", updates[0])
        self.assertIn("Temperature: 22 C", report)
        self.assertEqual(updates[-1], report)

    def test_weather_failure_does_not_discard_plan(self):
        with patch.object(supervisor, "get_weather", side_effect=RuntimeError("network")), patch.object(supervisor, "ask_gemini", return_value="# Itinerary\nDay 1: Museum"):
            result = supervisor.supervisor_agent("Paris", 1, "500", "Solo", "Art", "London")
        self.assertIn("Day 1: Museum", result)
        self.assertIn("Weather information unavailable", result)

    def test_long_trip_has_sufficient_output_budget_and_correct_nights(self):
        with patch.object(supervisor, "get_weather", return_value="unavailable"), patch.object(supervisor, "ask_gemini", return_value="Report") as call:
            supervisor.supervisor_agent("Tokyo", 30, "100000", "Solo", "Food", "Osaka")
        self.assertEqual(call.call_args.kwargs["max_output_tokens"], 6424)
        self.assertIn("hotel nights", call.call_args.args[0])
        self.assertIn("29", call.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
