import json
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from api import index

class WebApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(index.app)

    def trip(self):
        return {"destination":"Paris","days":3,"budget":"EUR 1500","travelers":"Solo","interests":"Art","departure":"London"}

    def test_home_static_and_health(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/static/app.js").status_code, 200)
        self.assertEqual(self.client.get("/api/health").json()["status"], "ok")

    def test_plan_stream_has_complete_event_and_timings(self):
        def generate(*args, on_chunk=None):
            on_chunk("# Itinerary\nDay 1")
            return "# Itinerary\nDay 1\n# Weather\nClear"
        with patch.object(index, "supervisor_agent", side_effect=generate):
            response = self.client.post("/api/plan", json=self.trip())
        events = [json.loads(line) for line in response.text.splitlines()]
        self.assertEqual(events[0]["type"], "text")
        self.assertEqual(events[-1]["type"], "done")
        self.assertIsNotNone(events[-1]["first_text_seconds"])
        self.assertEqual(response.headers["cache-control"], "no-store")

    def test_invalid_trip_is_rejected_before_model_call(self):
        trip = self.trip()
        trip["days"] = 31
        with patch.object(index, "supervisor_agent") as generate:
            self.assertEqual(self.client.post("/api/plan", json=trip).status_code, 422)
        generate.assert_not_called()

    def test_error_details_are_not_exposed(self):
        with patch.object(index, "supervisor_agent", side_effect=ValueError("private detail")):
            response = self.client.post("/api/plan", json=self.trip())
        self.assertNotIn("private detail", response.text)
        self.assertIn('"type": "error"', response.text)

    def test_busy_error_remains_user_friendly(self):
        with patch.object(index, "supervisor_agent", side_effect=RuntimeError("Gemini is temporarily busy")):
            response = self.client.post("/api/plan", json=self.trip())
        self.assertIn("temporarily busy", response.text)

    def test_chat_uses_saved_plan(self):
        with patch.object(index, "ask_followup", return_value="Use the metro") as chat:
            response = self.client.post("/api/chat", json={"plan":"Paris plan","question":"Transport?"})
        self.assertEqual(chat.call_args.args, ("Paris plan","Transport?"))
        self.assertIn('"type": "done"', response.text)

    def test_pdf_is_returned_in_memory_and_escapes_markup(self):
        response = self.client.post("/api/pdf", json={"plan":"# Plan\nMuseum <visit> & lunch"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b"%PDF"))
        self.assertEqual(response.headers["content-type"], "application/pdf")

    def test_unknown_map_is_not_silently_relocated(self):
        self.assertIsNone(self.client.get("/api/location?destination=Unknown").json()["coordinates"])
        self.assertEqual(self.client.get("/api/location?destination=Paris").json()["coordinates"], [48.8566,2.3522])

if __name__ == "__main__":
    unittest.main()
