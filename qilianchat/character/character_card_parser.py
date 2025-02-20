import os
import ssl
import struct
import zlib

import base64
import json
from pprint import pprint

import httpx


script_dir = os.path.dirname(__file__)
relative_json_path="..\\data\\character_cards\\json"
relative_card_path="..\\data\\character_cards\\card"


class CharacterCardParser:
    @staticmethod
    def encode_text_chunk(keyword, text):
        """创建 PNG 的 tEXt 块，包含关键词和文本数据"""
        chunk_data = keyword.encode('latin1') + b'\x00' + text.encode('latin1')
        return b'tEXt' + chunk_data

    @staticmethod
    def calculate_crc(chunk_type, data):
        """计算 PNG 块的 CRC 校验值"""
        return struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)

    @staticmethod
    def embed_character_card(image_path, output_path, character_data, format_version="V3"):
        """
        将角色卡数据嵌入 PNG 文件。
        :param image_path: 输入 PNG 文件路径
        :param output_path: 输出 PNG 文件路径
        :param character_data: 角色卡 JSON 数据
        :param format_version: 数据版本 (V3 或 V2)
        """
        with open(image_path, "rb") as img_file:
            png_data = img_file.read()

        # 检查文件是否为 PNG 格式
        if png_data[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError("输入文件不是有效的 PNG 文件")

        # 根据版本选择关键词
        character_chunk_keyword = "ccv3" if format_version.upper() == "V3" else "chara"
        # 将角色卡数据编码为 Base64 格式
        encoded_data = base64.b64encode(json.dumps(character_data).encode("utf-8")).decode("utf-8")
        # 创建 tEXt 块
        text_chunk = CharacterCardParser.encode_text_chunk(character_chunk_keyword, encoded_data)

        # 拆分 PNG 文件为块
        chunks = []
        i = 8
        while i < len(png_data):
            length = struct.unpack(">I", png_data[i:i+4])[0]
            chunk_type = png_data[i+4:i+8]
            chunk_data = png_data[i+8:i+8+length]
            crc = png_data[i+8+length:i+12+length]
            chunks.append((chunk_type, chunk_data, crc))
            i += 12 + length

        # 在 IEND 块之前插入角色卡数据块
        new_chunks = []
        for chunk_type, chunk_data, crc in chunks:
            if chunk_type == b"IEND":
                # 添加角色卡块
                new_chunks.append((b"tEXt", text_chunk, CharacterCardParser.calculate_crc(b"tEXt", text_chunk)))
            new_chunks.append((chunk_type, chunk_data, crc))

        # 写入新的 PNG 文件
        with open(output_path, "wb") as output_file:
            output_file.write(b"\x89PNG\r\n\x1a\n")  # PNG 文件头
            for chunk_type, chunk_data, crc in new_chunks:
                output_file.write(struct.pack(">I", len(chunk_data)))  # 块长度
                output_file.write(chunk_type)  # 块类型
                output_file.write(chunk_data)  # 块数据
                output_file.write(crc)  # 块 CRC

    @staticmethod
    def extract_character_card(image_path):
        """
        从 PNG 文件中提取角色卡数据。
        :param image_path: PNG 文件路径
        :return: 解码后的角色卡 JSON 数据
        """
        with open(image_path, "rb") as img_file:
            png_data = img_file.read()

        # 检查文件是否为 PNG 格式
        if png_data[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError("输入文件不是有效的 PNG 文件")

        # 遍历 PNG 文件块，寻找 tEXt 数据块
        i = 8
        while i < len(png_data):
            length = struct.unpack(">I", png_data[i:i+4])[0]
            chunk_type = png_data[i+4:i+8]
            chunk_data = png_data[i+8:i+8+length]
            i += 12 + length

            # 检查 tEXt 块类型
            if chunk_type == b"tEXt":
                text = chunk_data.decode("latin1")
                keyword, data = text.split("\x00", 1)


                if keyword in ["ccv3", "chara"]:
                    # 解码 Base64 数据并返回 JSON
                    decoded_data = base64.b64decode(data).decode("utf-8")
                    character_data = json.loads(decoded_data)

                    file_name=""
                    # 提取并返回角色卡的 name 属性
                    if "name" in character_data:
                        file_name= character_data["name"]
                    else:
                        raise ValueError("角色卡数据中未找到 'name' 属性")

                    #保存为json文件
                    with open(os.path.join(script_dir,relative_json_path,f"{file_name}.json"), 'w',encoding='utf-8') as card_json_file:
                        json.dump(json.loads(decoded_data), card_json_file,indent=4,ensure_ascii=False)
                    return json.loads(decoded_data)

        raise ValueError("PNG 文件中未找到角色卡数据")




    @staticmethod
    async def get_file_url(file_receiver,file_id: str) -> str:
        """
        获取文件下载链接
        :param file_id: 文件 ID
        :return: 文件 URL
        """
        from nonebot.adapters.onebot.v11 import Bot
        bot: Bot = file_receiver.bot
        response = await bot.call_api("get_file", file_id=file_id)
        return response.get("url")

    @staticmethod
    async def download_file(url: str, file_name: str):
        """
        下载文件并保存到指定文件夹
        :param url: 文件下载链接
        :param file_name: 文件名
        :param folder: 保存的文件夹路径
        """
        heads = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
        }

        save_path = os.path.join(script_dir, relative_card_path,f"{file_name}.png")

        ssl_context = ssl.create_default_context()
        ssl_context.set_ciphers('DEFAULT')
        ssl_context.options |= ssl.OP_NO_SSLv2
        ssl_context.options |= ssl.OP_NO_SSLv3
        ssl_context.options |= ssl.OP_NO_TLSv1
        ssl_context.options |= ssl.OP_NO_TLSv1_1
        ssl_context.options |= ssl.OP_NO_COMPRESSION
        async with httpx.AsyncClient(verify=ssl_context) as client:
            resp= await client.get(url, headers=heads)
            if resp.status_code == 200:
                if resp.content[:8] != b"\x89PNG\r\n\x1a\n":
                    raise ValueError("输入文件不是有效的 PNG 文件")
                with open(save_path, "wb") as f:
                    f.write(resp.content)
                print(f"文件已保存到 {save_path}")
                return save_path
            else:
                print(f"下载文件失败，HTTP 状态码: {resp.status_code}")


# 示例用法
if __name__ == "__main__":
    # 角色卡数据示例
    character_data = {
        "name": "Sakana",
        "description": "一个有趣且调皮的助理角色。",
        "version": "3.0"
    }

    # 嵌入角色卡数据
    CharacterCardParser.embed_character_card(
        r"C:\Users\hgl\Pictures\Camera Roll\Lingsha.png", r"C:\Users\hgl\Pictures\Saved Pictures\LingSha.png", character_data, format_version="V3"
    )

    # 提取角色卡数据
    extracted_data = CharacterCardParser.extract_character_card(r"C:\Users\hgl\Downloads\c7dcfbd3db56d5f9.png")
    #pprint(extracted_data, indent=4)
    print(json.dumps(extracted_data, indent=4, ensure_ascii=False))
