import unittest

from fastapi.testclient import TestClient

from app.main import app


class HealthCheckTests(unittest.TestCase):
    def test_health_returns_service_database_and_config_status(self):
        client = TestClient(app)

        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["code"], "ok")
        self.assertEqual(body["message"], "success")
        self.assertTrue(body["trace_id"])
        self.assertEqual(body["data"]["service"]["status"], "ok")
        self.assertEqual(body["data"]["database"]["status"], "ok")
        self.assertEqual(body["data"]["config"]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
