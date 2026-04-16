import unittest


class TestCase(unittest.TestCase):
    def setUp(self):
        from fastapi_startkit.application import app
        from fastapi.testclient import TestClient

        self.client = TestClient(app())

        if hasattr(self, "startTestRun"):
            self.startTestRun()

    def tearDown(self):
        pass
