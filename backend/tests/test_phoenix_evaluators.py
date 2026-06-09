import unittest

from fastapi.testclient import TestClient

from app.main import app


class PhoenixEvaluatorApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_list_evaluators(self):
        response = self.client.get("/api/ai/phoenix-evaluators")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("items", body)
        self.assertGreaterEqual(len(body["items"]), 4)

    def test_api_case_generation_evaluation(self):
        payload = {
            "evaluator": "hallucination",
            "question": "根据接口文档生成登录接口的测试 case。",
            "context": (
                "接口文档说明：POST /api/login，支持用户名密码登录、验证码登录。"
                "需要覆盖登录成功、空密码、错误密码、验证码失效。"
            ),
            "answer": (
                "建议生成以下接口 case：登录成功、空密码、错误密码、验证码失效、验证码登录。"
            ),
            "metadata": {"scene": "api_case_generation"},
        }

        response = self.client.post("/api/ai/phoenix-evaluators/evaluate", json=payload)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["evaluator"], "hallucination")
        self.assertEqual(body["label"], "not_hallucinated")
        self.assertTrue(body["passed"])

    def test_functional_case_generation_detects_hallucination(self):
        payload = {
            "evaluator": "hallucination",
            "question": "根据登录改版需求生成功能 case。",
            "context": (
                "需求文档仅提到密码登录、验证码登录、失败次数限制策略，"
                "没有提到生物识别或第三方刷脸登录。"
            ),
            "answer": (
                "建议生成功能 case：密码登录、验证码登录、指纹登录、人脸登录、"
                "连续失败 5 次锁定。"
            ),
            "metadata": {"scene": "functional_case_generation"},
        }

        response = self.client.post("/api/ai/phoenix-evaluators/evaluate", json=payload)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["label"], "hallucinated")
        self.assertFalse(body["passed"])
        self.assertTrue(body["missing_claims"])

    def test_daily_chat_answer_correctness(self):
        payload = {
            "evaluator": "qa_correctness",
            "question": "登录失败 5 次之后系统会怎样？",
            "reference": "连续失败 5 次后账号锁定 10 分钟，需要等待后重试。",
            "answer": "连续失败 5 次后账号会被锁定 10 分钟，之后才能再次尝试登录。",
            "metadata": {"scene": "daily_chat"},
        }

        response = self.client.post("/api/ai/phoenix-evaluators/evaluate", json=payload)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["evaluator"], "qa_correctness")
        self.assertIn(body["label"], ["correct", "partially_correct"])
        self.assertTrue(body["passed"])


if __name__ == "__main__":
    unittest.main()
