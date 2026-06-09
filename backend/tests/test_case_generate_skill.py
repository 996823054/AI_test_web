import unittest

from app.skills.case_generate_skill import CaseGenerateSkill


class CaseGenerateSkillTests(unittest.TestCase):
    def test_normalizes_case_to_team_test_case_template(self):
        skill = CaseGenerateSkill()

        result = skill.run(
            {
                "document": {"id": 1, "title": "登录需求"},
                "cases": [
                    {
                        "name": "登录成功",
                        "category": "positive",
                        "priority": "P0",
                        "precondition": "用户已注册",
                        "steps": ["输入账号密码", "点击登录"],
                        "expected_result": "进入首页",
                        "source_excerpt": "用户可以通过账号密码登录系统。",
                    }
                ],
            }
        )

        self.assertTrue(result["success"])
        case = result["data"]["cases"][0]
        self.assertEqual(case["case_no"], "TC-001")
        self.assertEqual(case["title"], "登录成功")
        self.assertEqual(case["requirement_ref"], "DOC-1 登录需求")
        self.assertEqual(case["importance"], "主路径")
        self.assertEqual(case["test_type"], "功能")
        self.assertEqual(case["test_data"], "账号密码等满足前置条件的数据")
        self.assertEqual(case["source_excerpt"], "用户可以通过账号密码登录系统。")
        self.assertGreaterEqual(len(case["steps"]), 3)
        case_format = result["data"]["case_format"]
        self.assertEqual(case_format["template"], "team_qa_case")
        self.assertEqual(case_format["columns"][0]["field"], "case_no")
        self.assertTrue(case_format["columns"][0]["required"])

    def test_formats_negative_few_shot_prompt_block(self):
        skill = CaseGenerateSkill()

        prompt_block = skill.format_negative_few_shots(
            [
                {
                    "chunk_text": "登录失败时提示错误",
                    "sample_payload": {"name": "错误用例", "steps": ["直接断言成功"]},
                    "rejection_category": "LOGIC_ERROR",
                    "user_feedback_comment": "没有覆盖失败提示",
                }
            ]
        )

        self.assertIn("### 过去被拒绝的错误用例模式", prompt_block)
        self.assertIn("登录失败时提示错误", prompt_block)
        self.assertIn("LOGIC_ERROR", prompt_block)
        self.assertIn("没有覆盖失败提示", prompt_block)


if __name__ == "__main__":
    unittest.main()
