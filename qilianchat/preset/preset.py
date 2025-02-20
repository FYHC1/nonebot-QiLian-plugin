import json

class Preset:
    def __init__(self, file_path):
        """初始化预设管理器，加载 JSON 文件"""
        self.file_path = file_path
        self.data = self._load_preset()

    def _load_preset(self):
        """从 JSON 文件加载预设"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"加载预设文件失败: {e}")
            return {}

    def save_preset(self):
        """保存修改后的预设数据到 JSON 文件"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存预设失败: {e}")

    def get_global_setting(self, key):
        """获取全局设置"""
        return self.data.get("global_settings", {}).get(key, None)

    def set_global_setting(self, key, value):
        """修改全局设置"""
        if "global_settings" in self.data:
            self.data["global_settings"][key] = value
        else:
            self.data["global_settings"] = {key: value}

    def get_prompts(self):
        return self.data["prompts"]

    def get_prompt_by_name(self, prompt_name):
        """获取指定名称的 prompt 配置"""
        return self.data.get("prompts", {}).get(prompt_name, None)

    def add_or_update_prompt(self, prompt_name, prompt_data):
        """添加或更新 prompt"""
        if "prompts" not in self.data:
            self.data["prompts"] = {}
        self.data["prompts"][prompt_name] = prompt_data

    def remove_prompt(self, prompt_name):
        """删除指定名称的 prompt"""
        if "prompts" in self.data and prompt_name in self.data["prompts"]:
            del self.data["prompts"][prompt_name]

# 示例使用：
if __name__ == "__main__":
    manager = Preset("preset1.json")

    # 获取一个全局设置
    print("当前温度参数:", manager.get_global_setting("temperature"))

    # 修改一个全局设置
    manager.set_global_setting("temperature", 1.2)
    manager.save_preset()

    # 获取一个 prompt
    prompt = manager.get_prompt_by_name("Main Prompt")
    if prompt:
        print("Main Prompt 内容:", prompt["content"])

    # 添加新 prompt
    new_prompt = {
        "name": "Test Prompt",
        "identifier": "test",
        "system_prompt": True,
        "role": "user",
        "content": "这是一个测试 prompt。",
        "injection_position": 1,
        "injection_depth": 3
    }
    manager.add_or_update_prompt("Test Prompt", new_prompt)
    manager.save_preset()
