import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from pprint import pprint

class SillyTavernPreset:
    """SillyTavern预设转换器类,用于转换和管理预设配置
    
    Attributes:
        script_dir (Path): 脚本所在目录
        data (Dict[str, Any]): 转换后的预设数据
    """

    def __init__(self, file_path: str) -> None:
        """初始化预设转换器
        
        Args:
            file_path: 预设文件路径
            
        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON格式错误
        """
        self.script_dir = Path(__file__).parent
        self.data = self._load_and_convert(file_path)

    def _load_and_convert(self, file_path: str) -> Dict[str, Any]:
        """加载并转换预设文件
        
        Args:
            file_path: 预设文件路径
            
        Returns:
            Dict[str, Any]: 转换后的预设数据
            
        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON格式错误
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"预设文件不存在: {file_path}")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            preset_data = {
                "global_settings": {},
                "prompts": {},
                "prompt_order": {},
            }

            # 处理全局设置
            for key, value in json_data.items():
                if key not in ["prompts", "prompt_order"]:
                    preset_data["global_settings"][key] = value

            # 处理提示词
            for prompt in json_data.get("prompts", []):
                name = prompt.get("name")
                if name:
                    preset_data["prompts"][name] = {
                        "name": name,
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

            # 处理提示词顺序
            for char_order in json_data.get("prompt_order", []):
                char_id = char_order.get("character_id")
                if char_id:
                    new_order = []
                    for item in char_order.get("order", []):
                        identifier = item.get("identifier")
                        if identifier:
                            for name, prompt_data in preset_data["prompts"].items():
                                if prompt_data.get("identifier") == identifier:
                                    new_order.append({
                                        "name": name,
                                        "identifier": identifier,
                                        "enabled": item.get("enabled")
                                    })
                                    break
                    preset_data["prompt_order"][char_id] = new_order

            return preset_data
            
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"预设文件格式错误: {str(e)}", e.doc, e.pos)

    def get_all_settings(self) -> Dict[str, Any]:
        """获取所有设置
        
        Returns:
            Dict[str, Any]: 所有设置数据
        """
        return self.data

    def get_all_prompts(self) -> str:
        """获取所有提示词设置
        
        Returns:
            str: JSON格式的提示词设置
        """
        return json.dumps(
            self.data.get("prompts", {}), 
            indent=4,
            ensure_ascii=False
        )

    def get_prompt_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """通过名称获取提示词设置
        
        Args:
            name: 提示词名称
            
        Returns:
            Optional[Dict[str, Any]]: 提示词设置,不存在则返回None
        """
        return self.data["prompts"].get(name)

    def get_prompt_order(self) -> Dict[str, Any]:
        """获取提示词顺序
        
        Returns:
            Dict[str, Any]: 提示词顺序配置
        """
        return self.data["prompt_order"]

    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串
        
        Args:
            indent: 缩进空格数
            
        Returns:
            str: JSON格式字符串
        """
        return json.dumps(
            self.data,
            indent=indent,
            ensure_ascii=False
        )

    def save_preset(self, file_name: str, file_type: str = "json") -> None:
        """保存预设到文件
        
        Args:
            file_name: 文件名(不含扩展名)
            file_type: 文件类型(扩展名)
            
        Raises:
            IOError: 保存失败
        """
        try:
            save_path = (
                self.script_dir / 
                f"../config/preset/QL_preset/{file_name}.{file_type}"
            )
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(self.to_json(indent=2))
                
        except IOError as e:
            raise IOError(f"保存预设失败: {str(e)}") from e


    def save_prompt_order(self,message_type:str,file_name:str,order:dict)->None:
        prompt_order_path=self.script_dir /f'../config/preset/preset_prompt_orders/{file_name}/{message_type}_prompt_order.json'
        with open(prompt_order_path, 'w', encoding='utf-8') as f:
            json.dump(order, f, indent=4, ensure_ascii=False)

    def print_pretty(self) -> None:
        """以易读格式打印数据"""
        pprint(self.data, indent=2)



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