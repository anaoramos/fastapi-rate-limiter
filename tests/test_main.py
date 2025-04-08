import unittest
from fastapi.testclient import TestClient

from main import app


class TestRateLimiter(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_user_can_make_5_requests(self):
        for _ in range(5):
            res = self.client.post("/ping", params={"user_id": "test_user"})
            self.assertEqual(res.status_code, 200)

        res = self.client.post("/ping", params={"user_id": "test_user"})
        self.assertEqual(res.status_code, 429)

    def test_retrieve_user_current_status(self):
        res = self.client.get("/status", params={"user_id": "test_user_2"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), 0)

        for _ in range(5):
            self.client.post("/ping", params={"user_id": "test_user_2"})

        res = self.client.get("/status", params={"user_id": "test_user_2"})
        self.assertEqual(res.json(), 5)
