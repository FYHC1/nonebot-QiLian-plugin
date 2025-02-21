from typing import List, Optional
from pathlib import Path
from .character_card import CharacterCard

class Character:
    """角色类,用于管理角色的基本信息和属性
    
    Attributes:
        name (str): 角色名称
        description (str): 角色描述
        personality (str): 角色性格特征
        mes_example (List[str]): 对话示例列表
        scenario (str): 场景设定
        first_message (str): 初始对话消息
        depth (int): 对话历史深度
    """

    def __init__(self, character_card_path: str) -> None:
        """初始化角色对象
        
        Args:
            character_card_path: 角色卡JSON文件路径
            
        Raises:
            FileNotFoundError: 角色卡文件不存在
            ValueError: 角色卡数据无效
        """
        try:
            character_card = CharacterCard.from_json(character_card_path)
            
            # 验证角色卡数据
            is_valid, message = character_card.validate()
            if not is_valid:
                raise ValueError(f"角色卡数据无效: {message}")
                
            self.name: str = character_card.get_character_name()
            self.description: str = character_card.get_description()
            self.personality: str = character_card.get_personality()
            self.mes_example: List[str] = character_card.get_mes_example()
            self.scenario: str = character_card.get_scenario()
            self.first_message: str = character_card.get_first_message()
            self.depth: int = character_card.get_depth()
            
        except FileNotFoundError:
            raise FileNotFoundError(f"角色卡文件不存在: {character_card_path}")
        except Exception as e:
            raise ValueError(f"加载角色卡时发生错误: {str(e)}")

    def get_name(self) -> str:
        """获取角色名称
        
        Returns:
            str: 角色名称
        """
        return self.name

    def get_description(self) -> str:
        """获取角色描述
        
        Returns:
            str: 角色描述
        """
        return self.description

    def get_personality(self) -> str:
        """获取角色性格特征
        
        Returns:
            str: 角色性格特征
        """
        return self.personality

    def get_mes_example(self) -> List[str]:
        """获取对话示例列表
        
        Returns:
            List[str]: 对话示例列表
        """
        return self.mes_example

    def get_scenario(self) -> str:
        """获取场景设定
        
        Returns:
            str: 场景设定
        """
        return self.scenario

    def get_first_message(self) -> str:
        """获取初始对话消息
        
        Returns:
            str: 初始对话消息
        """
        return self.first_message

    def get_depth(self) -> int:
        """获取对话历史深度
        
        Returns:
            int: 对话历史深度
        """
        return self.depth

    def get_character_info(self) -> dict:
        """获取角色完整信息
        
        Returns:
            dict: 包含角色所有属性的字典
        """
        return {
            "name": self.name,
            "description": self.description,
            "personality": self.personality,
            "scenario": self.scenario,
            "first_message": self.first_message,
            "depth": self.depth,
            "mes_example_count": len(self.mes_example)
        }

    def update_character(self, **kwargs) -> None:
        """更新角色属性
        
        Args:
            **kwargs: 要更新的属性键值对
            
        Raises:
            AttributeError: 属性不存在
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"Character没有属性: {key}")

if __name__ == '__main__':
    try:
        character = Character(r"D:\CodeDocument\PythonDocument\QiLianBot\QiLianBot2\plugins\qilianchat\data\character_cards\json\莉莉雅.json")
        print(character.get_name())
        print(character.get_description())
        print(character.get_personality())
    except Exception as e:
        print(f"Error: {str(e)}")