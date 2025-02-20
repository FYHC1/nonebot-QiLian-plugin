import json
from copy import deepcopy


class CharacterCard:
    def __init__(self, spec, spec_version, data):
        self.spec = spec
        self.spec_version = spec_version
        self.data = data
        self.history = []

    # 1. 基本信息获取
    def get_character_name(self)->str:
        return self.data.get("name", "")

    def get_description(self):
        return self.data.get("description", "")

    def get_personality(self):
        return self.data.get("personality", "")

    def get_mes_example(self):
        return self.data.get("mes_example", "")

    def get_scenario(self):
        return self.data.get("scenario", "")

    def get_first_message(self):
        return self.data.get("first_mes", "")

    def get_depth(self):
        return self.data["extensions"]["depth_prompt"]["depth"]


    # 2. 高级功能 - 字段编辑
    def set_character_name(self, name):
        self.data["name"] = name

    def set_description(self, description):
        self.data["description"] = description

    def set_personality(self, personality):
        self.data["personality"] = personality

    def set_mes_example(self, example):
        self.data["mes_example"] = example

    def set_scenario(self, scenario):
        self.data["scenario"] = scenario

    def set_depth(self,depth):
        self.data["extensions"]["depth_prompt"]["depth"]=depth

    # 3. 嵌套字段操作
    def get_from_character_book(self):
        return self.data.get("character_book", "")

    def add_to_character_book(self, entry):
        if "character_book" not in self.data:
            self.data["character_book"] = {"entries": []}
        self.data["character_book"]["entries"].append(entry)

    def remove_from_character_book(self, entry_id):
        if "character_book" in self.data:
            self.data["character_book"]["entries"] = [
                entry for entry in self.data["character_book"]["entries"] if entry["id"] != entry_id
            ]

    # 3.1 嵌套字段高级操作
    def add_extension(self, key, value):
        if "extensions" not in self.data:
            self.data["extensions"] = {}
        self.data["extensions"][key] = value

    def remove_extension(self, key):
        if "extensions" in self.data and key in self.data["extensions"]:
            del self.data["extensions"][key]

    def modify_character_book_entry(self, entry_id, updated_content):
        """通过 entry_id 修改 character_book 条目"""
        if "character_book" in self.data and "entries" in self.data["character_book"]:
            for entry in self.data["character_book"]["entries"]:
                if entry["id"] == entry_id:
                    self._record_history("character_book", deepcopy(entry))
                    entry.update(updated_content)
                    return
        raise ValueError(f"Entry with ID {entry_id} not found.")

    def find_character_book_entry(self, keyword):
        """通过关键字查找 character_book 条目"""
        if "character_book" in self.data and "entries" in self.data["character_book"]:
            return [
                entry for entry in self.data["character_book"]["entries"]
                if keyword in entry.get("content", "") or keyword in " ".join(entry.get("keys", []))
            ]
        return []

    # 4. 文件导入与导出
    @staticmethod
    def from_json(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return CharacterCard(
            spec=data.get("spec", ""),
            spec_version=data.get("spec_version", ""),
            data=data.get("data", {})
        )

    def to_json(self, file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump({
                "spec": self.spec,
                "spec_version": self.spec_version,
                "data": self.data
            }, file, ensure_ascii=False, indent=4)

    # 5. 验证机制
    def validate(self):
        required_fields = ["spec", "spec_version", "data"]
        for field in required_fields:
            if not getattr(self, field, None):
                return False, f"Missing required field: {field}"
        if not isinstance(self.data.get("name"), str):
            return False, "Character name must be a string"
        return True, "Validation passed"

    # 6. 格式化输出
    def display_summary(self):
        summary = {
            #"name": self.get_character_name(),
            "description": self.get_description(),
            "personality": self.get_personality(),
            "scenario": self.get_scenario(),
            "first_mes": self.get_first_message(),
        }
        #return json.dumps(summary, indent=4, ensure_ascii=False)
        return summary

    # 静态方法 - 从字典构建对象
    @staticmethod
    def from_dict(data_dict):
        return CharacterCard(
            spec=data_dict.get("spec", ""),
            spec_version=data_dict.get("spec_version", ""),
            data=data_dict.get("data", {})
        )


    def _record_history(self, field, previous_value):
        """记录更改历史"""
        self.history.append({
            "field": field,
            "previous_value": previous_value
        })

    def rollback_last_change(self):
        """回滚最后一次更改"""
        if not self.history:
            raise ValueError("No changes to rollback.")
        last_change = self.history.pop()
        field, previous_value = last_change["field"], last_change["previous_value"]
        if field in self.data:
            self.data[field] = previous_value


# 使用示例
if __name__ == "__main__":
    # 从 JSON 文件加载角色卡
    sakana_card = CharacterCard.from_json(r"D:\CodeDocument\PythonDocument\QiLianBot\QiLianBot\plugins\nonebot_sillytavern_plugin\data\character_cards\json\Sakana.json")

    # 查看角色摘要
    print(sakana_card.display_summary())

    # # 修改角色属性
    # sakana_card.set_character_name("Sakana New Name")
    # sakana_card.set_description("A modified description.")

    # 添加嵌套字段
    sakana_card.add_to_character_book({
        "id": 99,
        "keys": ["example"],
        "content": "This is a new entry for the character book."
    })

    # 导出修改后的角色卡
    sakana_card.to_json("Sakana_Modified.json")

    # 验证角色卡
    is_valid, message = sakana_card.validate()
    print("Validation:", message)
