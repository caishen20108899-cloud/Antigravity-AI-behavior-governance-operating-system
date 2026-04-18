import json
import os
from .event_logger import log_event

class QuestionTuner:
    """
    gstack 风格的 Question Tuning (提问偏好学习与拦截系统)
    拦截频繁相同类型的打扰问题，依据历史用户偏好完成 AUTO_DECIDE
    """
    def __init__(self, project_cwd):
        self.prefs_file = os.path.join(project_cwd, ".ag_preferences.json")
        self.preferences = self._load_prefs()
        
    def _load_prefs(self):
        if os.path.exists(self.prefs_file):
            try:
                with open(self.prefs_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_prefs(self):
        try:
            with open(self.prefs_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_event("@Commander", "MessageError", f"⚠️ 偏好保存失败: {e}")

    def teach_preference(self, category: str, action: str):
        """记录用户的强制偏好 (如 'linting', 'always_auto_fix')"""
        # 防止毒性数据写入：只有明确指派的来源可以污染此配置
        if category in ["delete_db", "modify_auth", "deploy_prod"]:
            log_event("@Commander", "MessageError", f"🔴 [安全围网] 系统级限制：禁止通过偏好自动绕过高危分类 ({category}) 的人工审批！")
            return False
            
        self.preferences[category] = action
        self._save_prefs()
        log_event("@Commander", "MessageStatus", f"🧠 [Question Tuning] 已将偏好持久化: 遇到类目 '{category}' 将默认执行 -> '{action}'")
        return True

    def tune_question(self, question_id: str, default_options: list) -> str:
        """
        拦截预提问。
        如果该分类已被 teach_preference 收录，自动执行并返回结果。
        如果不受信任，则返回 ASK 标识。
        """
        if question_id in self.preferences:
            decision = self.preferences[question_id]
            log_event("@Commander", "MessageToolResult", 
                     f"🤖 [Question Tuning AUTO_DECIDE]: 命中 '{question_id}' 拦截规则，已自动代替指挥官选择 -> 【{decision}】。")
            return decision
            
        return "ASK_NORMALLY"

if __name__ == "__main__":
    tuner = QuestionTuner(".")
    tuner.teach_preference("linting", "A (Auto-fix all format issues)")
    tuner.teach_preference("modify_auth", "Always approve")  # 此操作应该被高敏拦截
    print("决策结果:", tuner.tune_question("linting", []))
    print("未收录结果:", tuner.tune_question("add_feature", []))
