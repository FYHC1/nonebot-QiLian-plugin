import json
import pprint


class SillyTavernPreset:
    def __init__(self, file_path):
        """
        从 JSON 文件加载并转换 SillyTavern 预设数据。

        Args:
            file_path (str): 预设文件的路径。
        """
        self.data = self._load_and_convert(file_path)

    def _load_and_convert(self, file_path):
        """
         加载 JSON 文件并转换为内部使用的 Python 字典结构。
         """
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # 初始化转换后的字典结构
        preset_data = {
            "global_settings": {},
            "prompts": {},
            "prompt_order": {},
        }

        # 处理全局设置
        for key, value in json_data.items():
            if key not in ["prompts", "prompt_order"]:
                preset_data["global_settings"][key] = value

        # 处理 prompts
        for prompt in json_data.get("prompts", []):
            name = prompt.get("name")
            if name:  # 确保name存在
                preset_data["prompts"][name] = {
                    "name": name,  # 存储 name
                    "identifier": prompt.get("identifier"),
                    "system_prompt": prompt.get("system_prompt"),
                    "role": prompt.get("role"),
                    "content": prompt.get("content"),
                    "injection_position": prompt.get("injection_position"),
                    "injection_depth": prompt.get("injection_depth"),
                    "forbid_overrides": prompt.get("forbid_overrides"),
                    "marker": prompt.get("marker"),
                    "enabled": prompt.get("enabled")
                }

        # 处理 prompt_order
        for char_order in json_data.get("prompt_order", []):
            char_id = char_order.get("character_id")
            if char_id:  # 确保character_id存在
                new_order = []
                for item in char_order.get("order", []):
                        identifier = item.get("identifier")
                        if identifier:  # 确保identifier存在
                            # 通过identifier找到对应的name
                            for name, prompt_data in preset_data["prompts"].items():
                                if prompt_data.get("identifier") == identifier:
                                    new_order.append({
                                        "name": name,
                                        "identifier": identifier,
                                        "enabled": item.get("enabled")
                                    })
                                    break  # 找到就跳出循环

                preset_data["prompt_order"][char_id] = new_order

        return preset_data

    def get_all_settings(self):
        """返回所有的设置"""
        return self.data


    def get_all_prompts(self):
        """返回所有 prompt 设置"""
        return json.dumps(self.data.get("prompts", {}), indent=4,ensure_ascii=False)

    def get_prompt_by_name(self, name):
        """通过 name 返回 prompt 设置"""
        return self.data["prompts"].get(name)

    def get_prompt_order(self):
        """ 返回指定角色的 prompt 加载顺序"""
        return self.data["prompt_order"]

    def to_json(self, indent=2):
        """以 JSON 格式返回转换后的数据。"""
        return json.dumps(self.data, indent=indent, ensure_ascii=False)

    def print_pretty(self):
        """ 打印转换后的数据。"""
        pprint.pprint(self.data, indent=2)



if __name__ == '__main__':
    file_path = r"C:\Users\hgl\Downloads\Ac_markdown无界域.json"
    preset1 = SillyTavernPreset(file_path)

    # file_path2 = "Ac_markdown无界域.json"
    # preset2 = SillyTavernPreset(file_path2)
    #
    # print("预设1 模型设置:")
    # print(preset1.get_model_settings())
    #
    # print("\n预设2 模型设置:")
    # print(preset2.get_model_settings())
    #
    # print("\n预设1 所有prompts:")
    # print(preset1.get_all_prompts())
    #
    # print("\n预设2 所有prompts:")
    # print(preset2.get_all_prompts())

    print(preset1.to_json())