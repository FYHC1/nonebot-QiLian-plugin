import json
from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime


class CharacterCard:
    """角色卡类,用于管理角色卡数据
    
    Attributes:
        spec (str): 规格说明
        spec_version (str): 规格版本
        data (Dict): 角色卡数据
        history (List): 修改历史
    """

    def __init__(self, spec: str, spec_version: str, data: Dict[str, Any]) -> None:
        """初始化角色卡对象
        
        Args:
            spec (str): 规格说明
            spec_version (str): 规格版本 
            data (Dict[str, Any]): 角色卡数据
        """
        self.spec: str = spec
        self.spec_version: str = spec_version
        self.data: Dict[str, Any] = data
        self.history: List[Dict[str, Any]] = []

    # 1. 基本信息获取
    def get_character_name(self) -> str:
        """获取角色名称
        
        Returns:
            str: 角色名称
        """
        return self.data.get("name", "")

    def get_description(self) -> str:
        """获取角色描述
        
        Returns:
            str: 角色描述
        """
        return self.data.get("description", "")

    def get_personality(self) -> str:
        """获取角色性格
        
        Returns:
            str: 角色性格特征描述
        """
        return self.data.get("personality", "")

    def get_mes_example(self) -> List[str]:
        """获取对话示例列表
        
        Returns:
            List[str]: 对话示例列表
        """
        return self.data.get("mes_example", [])

    def get_scenario(self) -> str:
        """获取场景设定
        
        Returns:
            str: 场景设定描述
        """
        return self.data.get("scenario", "")

    def get_first_message(self) -> str:
        """获取初始消息
        
        Returns:
            str: 角色的初始对话消息
        """
        return self.data.get("first_mes", "")

    def get_depth(self) -> int:
        """获取对话深度设置
        
        Returns:
            int: 对话深度值
            
        Raises:
            KeyError: 深度设置不存在时抛出
        """
        try:
            return self.data["extensions"]["depth_prompt"]["depth"]
        except KeyError as e:
            raise KeyError("深度设置不存在") from e


    # 2. 高级功能 - 字段编辑
    def set_character_name(self, name: str) -> None:
        """设置角色名称
        
        Args:
            name (str): 新的角色名称
        """
        self._record_history("name", self.data.get("name"))
        self.data["name"] = name

    def set_description(self, description: str) -> None:
        """设置角色描述
        
        Args:
            description (str): 新的角色描述
        """
        self._record_history("description", self.data.get("description"))
        self.data["description"] = description

    def set_personality(self, personality: str) -> None:
        """设置角色性格
        
        Args:
            personality (str): 新的性格描述
        """
        self._record_history("personality", self.data.get("personality"))
        self.data["personality"] = personality

    def set_mes_example(self, example: List[str]) -> None:
        """设置对话示例
        
        Args:
            example (List[str]): 新的对话示例列表
        """
        self._record_history("mes_example", self.data.get("mes_example"))
        self.data["mes_example"] = example

    def set_scenario(self, scenario: str) -> None:
        """设置场景描述
        
        Args:
            scenario (str): 新的场景描述
        """
        self._record_history("scenario", self.data.get("scenario"))
        self.data["scenario"] = scenario

    def set_depth(self, depth: int) -> None:
        """设置对话深度
        
        Args:
            depth (int): 新的对话深度值
            
        Raises:
            KeyError: extensions或depth_prompt不存在时抛出
        """
        try:
            self._record_history("depth", self.data["extensions"]["depth_prompt"]["depth"])
            self.data["extensions"]["depth_prompt"]["depth"] = depth
        except KeyError as e:
            raise KeyError("深度设置路径不存在") from e

    # 3. 嵌套字段操作
    def get_from_character_book(self) -> Dict[str, Any]:
        """获取角色书籍数据
        
        Returns:
            Dict[str, Any]: 角色书籍数据
        """
        return self.data.get("character_book", {})

    def add_to_character_book(self, entry: Dict[str, Any]) -> None:
        """添加条目到角色书籍
        
        Args:
            entry (Dict[str, Any]): 要添加的条目数据
        """
        if "character_book" not in self.data:
            self.data["character_book"] = {"entries": []}
        self._record_history("character_book_entries", 
                           self.data["character_book"]["entries"].copy())
        self.data["character_book"]["entries"].append(entry)

    def remove_from_character_book(self, entry_id: int) -> None:
        """从角色书籍中移除指定条目
        
        Args:
            entry_id (int): 要移除的条目ID
        """
        if "character_book" in self.data:
            self._record_history("character_book_entries", 
                               self.data["character_book"]["entries"].copy())
            self.data["character_book"]["entries"] = [
                entry for entry in self.data["character_book"]["entries"] 
                if entry["id"] != entry_id
            ]

    # 3.1 嵌套字段高级操作
    def add_extension(self, key: str, value: Any) -> None:
        """添加扩展数据
        
        Args:
            key (str): 扩展键名
            value (Any): 扩展值
        """
        if "extensions" not in self.data:
            self.data["extensions"] = {}
        self._record_history(f"extension_{key}", self.data["extensions"].get(key))
        self.data["extensions"][key] = value

    def remove_extension(self, key: str) -> None:
        """移除扩展数据
        
        Args:
            key (str): 要移除的扩展键名
            
        Raises:
            KeyError: 扩展键不存在时抛出
        """
        if "extensions" in self.data and key in self.data["extensions"]:
            self._record_history(f"extension_{key}", self.data["extensions"][key])
            del self.data["extensions"][key]
        else:
            raise KeyError(f"扩展键 {key} 不存在")

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
    def from_json(file_path: Union[str, Path]) -> "CharacterCard":
        """从JSON文件加载角色卡
        
        Args:
            file_path (Union[str, Path]): JSON文件路径
            
        Returns:
            CharacterCard: 角色卡对象
            
        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON格式错误
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return CharacterCard(
                spec=data.get("spec", ""),
                spec_version=data.get("spec_version", ""),
                data=data.get("data", {})
            )
        except FileNotFoundError as e:
            raise FileNotFoundError(f"角色卡文件不存在: {file_path}") from e
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"角色卡JSON格式错误: {str(e)}", e.doc, e.pos)

    def to_json(self, file_path: Union[str, Path]) -> None:
        """保存角色卡到JSON文件
        
        Args:
            file_path (Union[str, Path]): 保存路径
            
        Raises:
            IOError: 写入文件失败
        """
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump({
                    "spec": self.spec,
                    "spec_version": self.spec_version,
                    "data": self.data
                }, file, ensure_ascii=False, indent=4)
        except IOError as e:
            raise IOError(f"保存角色卡失败: {str(e)}") from e

    # 5. 验证机制
    def validate(self) -> Tuple[bool, str]:
        """验证角色卡数据
        
        Returns:
            Tuple[bool, str]: (是否有效, 验证消息)
        """
        required_fields = ["spec", "spec_version", "data"]
        for field in required_fields:
            if not getattr(self, field, None):
                return False, f"缺少必需字段: {field}"
        if not isinstance(self.data.get("name"), str):
            return False, "角色名称必须是字符串"
        return True, "验证通过"

    # 6. 格式化输出
    def display_summary(self) -> Dict[str, str]:
        """显示角色卡摘要信息
        
        Returns:
            Dict[str, str]: 包含主要信息的摘要字典
        """
        return {
            "description": self.get_description(),
            "personality": self.get_personality(),
            "scenario": self.get_scenario(),
            "first_mes": self.get_first_message(),
        }

    # 静态方法 - 从字典构建对象
    @staticmethod
    def from_dict(data_dict: Dict[str, Any]) -> "CharacterCard":
        """从字典创建角色卡对象
        
        Args:
            data_dict (Dict[str, Any]): 包含角色卡数据的字典
            
        Returns:
            CharacterCard: 新创建的角色卡对象
            
        Raises:
            ValueError: 必需字段缺失时抛出
        """
        required = ["spec", "spec_version", "data"]
        if not all(field in data_dict for field in required):
            raise ValueError(f"缺少必需字段: {', '.join(required)}")
            
        return CharacterCard(
            spec=data_dict.get("spec", ""),
            spec_version=data_dict.get("spec_version", ""),
            data=data_dict.get("data", {})
        )


    def _record_history(self, field: str, previous_value: Any) -> None:
        """记录字段修改历史
        
        Args:
            field (str): 修改的字段名
            previous_value (Any): 修改前的值
        """
        self.history.append({
            "field": field,
            "previous_value": previous_value,
            "timestamp": datetime.now().isoformat()
        })

    def rollback_last_change(self) -> None:
        """回滚最后一次修改
        
        Raises:
            ValueError: 没有可回滚的修改记录时抛出
        """
        if not self.history:
            raise ValueError("没有可回滚的修改记录")
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
