import json
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple

class QLPreset:
    """七链预设管理类,用于管理预设配置
    
    Attributes:
        file_path (Path): 预设文件路径
        data (Dict[str, Any]): 预设数据
    """

    def __init__(self, file_path: Union[str, Path]) -> None:
        """初始化预设管理器
        
        Args:
            file_path: 预设文件路径
            
        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON格式错误
        """
        self.file_path = Path(file_path)
        self.data = self._load_preset()

    def _load_preset(self) -> Dict[str, Any]:
        """从JSON文件加载预设
        
        Returns:
            Dict[str, Any]: 预设数据
            
        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON格式错误
        """
        try:
            if not self.file_path.exists():
                raise FileNotFoundError(f"预设文件不存在: {self.file_path}")
                
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
                
        except FileNotFoundError:
            raise
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"预设文件格式错误: {str(e)}", 
                e.doc, 
                e.pos
            )

    def save_preset(self) -> None:
        """保存预设数据到JSON文件
        
        Raises:
            IOError: 保存失败
        """
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
                
        except IOError as e:
            raise IOError(f"保存预设失败: {str(e)}") from e

    def get_global_setting(self, key: str) -> Optional[Any]:
        """获取全局设置值
        
        Args:
            key: 设置键名
            
        Returns:
            Optional[Any]: 设置值,不存在则返回None
        """
        return self.data.get("global_settings", {}).get(key)

    def set_global_setting(self, key: str, value: Any) -> None:
        """设置全局设置值
        
        Args:
            key: 设置键名
            value: 设置值
        """
        if "global_settings" not in self.data:
            self.data["global_settings"] = {}
        self.data["global_settings"][key] = value

    def get_prompts(self) -> Dict[str, Any]:
        """获取所有提示词配置
        
        Returns:
            Dict[str, Any]: 提示词配置字典
        """
        return self.data.get("prompts", {})

    def get_prompt_by_name(self, prompt_name: str) -> Optional[Dict[str, Any]]:
        """获取指定名称的提示词配置
        
        Args:
            prompt_name: 提示词名称
            
        Returns:
            Optional[Dict[str, Any]]: 提示词配置,不存在则返回None
        """
        return self.data.get("prompts", {}).get(prompt_name)

    def add_or_update_prompt(self, prompt_name: str, prompt_data: Dict[str, Any]) -> None:
        """添加或更新提示词配置
        
        Args:
            prompt_name: 提示词名称
            prompt_data: 提示词配置数据
        """
        if "prompts" not in self.data:
            self.data["prompts"] = {}
        self.data["prompts"][prompt_name] = prompt_data

    def remove_prompt(self, prompt_name: str) -> bool:
        """删除指定名称的提示词
        
        Args:
            prompt_name: 提示词名称
            
        Returns:
            bool: 是否成功删除
        """
        if "prompts" in self.data and prompt_name in self.data["prompts"]:
            del self.data["prompts"][prompt_name]
            return True
        return False

    def validate_prompt_data(self, prompt_data: Dict[str, Any]) -> Tuple[bool, str]:
        """验证提示词配置数据有效性
        
        Args:
            prompt_data: 提示词配置数据
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        required_fields = ["name", "identifier", "role", "content"]
        for field in required_fields:
            if field not in prompt_data:
                return False, f"缺少必需字段: {field}"
                
        if not isinstance(prompt_data["content"], str):
            return False, "content必须是字符串"
            
        return True, "验证通过"

    def get_preset_info(self) -> Dict[str, Any]:
        """获取预设信息摘要
        
        Returns:
            Dict[str, Any]: 预设信息字典
        """
        return {
            "file_path": str(self.file_path),
            "prompt_count": len(self.get_prompts()),
            "global_settings": self.data.get("global_settings", {})
        }

# 示例使用：
if __name__ == "__main__":
    manager = QLPreset("preset1.json")

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
