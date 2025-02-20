import json
import os
from urllib.parse import urlparse, parse_qs

import requests
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.plugin.on import on_startswith, on_command, on_message
from nonebot.rule import to_me

from .character.character import Character  # Unused import, can be removed
from .character.character_card_parser import CharacterCardParser
from .chat.chat import Chat
from .chat.chat_session import ChatSession
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="QiLianChat",
    description="一个基于OneBot11的聊天插件，支持角色扮演、预设和多种聊天服务。",  # Added description
    usage="""
**触发关键词:** 怜祈
**帮助命令:** 怜祈 帮助

**普通用户指令:**
- @Bot + 消息内容 (群聊角色扮演)
- 消息内容 (私聊角色扮演)

**Superuser 指令:** (使用前请确保您是机器人 Superuser)
- 查看角色列表
- 指定聊天角色 <角色名>
- 上传角色卡 (回复图片消息 或 发送命令后上传图片/json文件)
- 查看预设列表
- 上传预设 (回复json文件消息 或 发送命令后上传json文件)
- 设置预设 <预设名>
- clear
- 设置聊天服务来源 <来源类型> (OpenAI, Claude, Google AI Studio, DeepSeek, Others)
- 设置代理url <URL>
- 设置代理密钥 <密钥>
- 设置模型 <模型名称>
- 设置max_tokens <正整数>
- 设置temperature <0~2浮点数>
""", # Improved usage
    config=Config,
)

from .messages.messages import Messages
from .open_ai.open_ai import Open_Ai
from .preset.RegexProcess import RegexProcessor
from .preset.preset_convert import SillyTavernPreset
from .preset.preset_manage import PresetManage

from .util.character_util import CharacterUtil
from .util.chat_util import ChatUtil

# 实例对象
char_util = CharacterUtil()
chat = Chat()
chat_util = ChatUtil()
messages = Messages()
regex_process = RegexProcessor()
open_ai = Open_Ai()
character_list = char_util.get_character_card_list()


# 触发词，保持插件运行
trigger_command = on_startswith(("怜祈"), ignorecase=True, priority=1, block=True) # Improved priority and block
@trigger_command.handle()
async def lian_qi():
    await trigger_command.finish("怜祈正在运行中") # More user-friendly message


# 帮助命令
help_command = on_command("怜祈 帮助", priority=1, block=True)
@help_command.handle()
async def handle_help():
    help_message = """
**怜祈 插件帮助**

**触发关键词:** `怜祈` (保持插件运行)

**角色管理 (Superuser 权限):**
- `查看角色列表`: 查看当前已加载的角色卡列表。
- `指定聊天角色 <角色名>`: 指定当前群聊/私聊的角色。
- `上传角色卡` (回复图片消息): 上传角色卡图片以添加新角色。
- `上传角色卡` (发送命令后上传图片/json文件): 上传角色卡图片或 JSON 文件以添加新角色。

**预设管理 (Superuser 权限):**
- `查看预设列表`: 查看当前已加载的预设列表。
- `上传预设` (回复json文件消息): 上传 SillyTavern 预设 JSON 文件。
- `上传预设` (发送命令后上传json文件): 上传 SillyTavern 预设 JSON 文件。
- `设置预设 <预设名>`: 设置当前群聊/私聊使用的预设。

**聊天管理 (Superuser 权限):**
- `clear`: 清空当前群聊/私聊的角色聊天记忆。

**OpenAI/模型设置 (Superuser 权限):**
- `设置聊天服务来源 <来源类型>`: 设置文本补全服务来源，可选: OpenAI, Claude, Google AI Studio, DeepSeek, Others。
- `设置代理url <URL>`: 设置 API 代理 URL。
- `设置代理密钥 <密钥>`: 设置 API 密钥。
- `设置模型 <模型名称>`: 设置使用的模型名称。
- `设置max_tokens <正整数>`: 设置模型生成回复的最大令牌数。
- `设置temperature <0~2浮点数>`: 设置模型 temperature 参数，影响生成回复的随机性。

**聊天互动:**
- 在群聊中 `@Bot + 消息内容` 即可进行角色扮演对话。
- 在私聊中 `直接发送消息内容` 即可进行角色扮演对话。
"""
    await help_command.finish(help_message)


# 查看角色列表
check_characters = on_command("查看角色列表", permission=SUPERUSER, priority=5, block=True) # Added priority and block
@check_characters.handle()
async def check_characters_list():
    characters = char_util.get_character_card_list() # More descriptive variable name
    await check_characters.finish(str(characters))


# 指定聊天角色
appoint_character = on_command("指定聊天角色", permission=SUPERUSER, priority=5, block=True) # Added priority and block
@appoint_character.handle()
async def appoint_chat_character(event: MessageEvent, args: Message = CommandArg()):
    message_type = event.message_type
    character_name = args.extract_plain_text().strip() # Stripped whitespace
    chat_session_id = str(event.group_id if message_type == "group" else event.user_id) # Simplified session ID logic

    if character_name not in character_list:
        await appoint_character.finish("不存在此角色，请重新指定角色") # Use await for finish
    await char_util.appoint_character(message_type, character_name, chat_session_id)
    await appoint_character.send(f"已指定聊天角色 {character_name}")
    #await chat.new_chat()
    char_util.set_init()


# 进行角色扮演对话
def is_group_message_to_me(event: MessageEvent): # More descriptive function name
    return event.message_type == "group" and to_me()(event) and not event.get_plaintext().startswith('/') # Combined conditions

def is_private_message(event: MessageEvent): # More descriptive function name
    return event.message_type == "private"

role_play = on_message(rule=is_group_message_to_me, priority=10, block=True)
role_play1 = on_message(rule=is_private_message, priority=10, block=True) # Keep role_play1 for clarity, can be merged if needed

async def handle_role_play(event: MessageEvent, bot: Bot, message_type: str, chat_user_id: str): # Centralized chat logic
    message = event.get_plaintext()
    if message_type == "group":
        chat_session = chat_util.get_group_session(chat_user_id)
    else:
        chat_session = chat_util.get_private_session(chat_user_id)

    if not chat_session:
        character = char_util.get_character_by_id(message_type, chat_user_id)
        chat_util.preset_manage.set_preset_config(message_type, chat_user_id, "Gemini!_It's_MyGO!!!!!_1.9.2版") # Default preset
        chat_session = chat_util.assign_session(message_type, character, chat_user_id)
        chat_session.set_user_id(str(event.user_id)) # Ensure user_id is set even for group chats
        chat_session.set_preset_regex(regex_process.get_patterns(chat_session.preset_name))
        if message_type == "group":
            chat_util.set_group_session(chat_user_id, chat_session)
        else:
            chat_util.set_private_session(chat_user_id, chat_session)

    chat_session.set_nick_name(await chat_util.get_nick_name(bot, str(event.user_id))) # Pass user_id as string
    chat_history = await chat.get_context(message_type, chat_user_id, chat_session.get_character_name())
    chat_messages = await messages.construct_messages(message, chat_session, chat_history)
    assistant_reply = await open_ai.start_chat(chat_messages)

    assistant_reply = "\n" + regex_process.process_by_regex(chat_session.get_preset_regex(), assistant_reply)
    await chat.save_chat_message(message_type, chat_user_id, chat_session.get_nick_name(), chat_session.get_character_name(), message, assistant_reply)
    return assistant_reply, str(event.user_id) # Return reply and user_id


@role_play.handle()
async def group_chat(event: MessageEvent, bot: Bot):
    message_type = event.message_type
    group_id = str(event.group_id)
    assistant_reply, user_id = await handle_role_play(event, bot, message_type, group_id) # Call centralized function
    await role_play.finish(MessageSegment.at(user_id) + Message(assistant_reply))


@role_play1.handle()
async def private_chat(event: MessageEvent, bot: Bot):
    message_type = event.message_type
    user_id = str(event.user_id)
    assistant_reply, user_id = await handle_role_play(event, bot, message_type, user_id) # Call centralized function
    await role_play1.finish(MessageSegment.at(user_id) + Message(assistant_reply))


# 清空聊天记录
clear_chat = on_command("clear", permission=SUPERUSER, priority=5, block=True) # Added priority and block
@clear_chat.handle()
async def clear_chat_message(event: MessageEvent):
    message_type = event.message_type
    chat_user_id = str(event.group_id if message_type == "group" else event.user_id) # Simplified user ID logic

    character_name = char_util.get_character_name(message_type, chat_user_id)
    await chat.clear_chat_message(message_type, chat_user_id, character_name)
    await clear_chat.finish("记忆已清除...")


# 添加角色卡
append_character_card = on_command("上传角色卡", permission=SUPERUSER, priority=5, block=True) # Added priority and block
@append_character_card.handle()
async def handle_file(event: MessageEvent, bot: Bot):
    character_card_parser = CharacterCardParser()
    for segment in event.message:
        if segment.type == "image":
            image_url = segment.data["url"]
            parsed_url = urlparse(image_url)
            query_params = parse_qs(parsed_url.query)
            file_name = query_params.get("fileid", [None])[0]

            if image_url and file_name: # Added file_name check
                try:
                    img_path = await character_card_parser.download_file(image_url, file_name)
                    character_card_parser.extract_character_card(img_path)
                    await append_character_card.send(str(char_util.get_character_card_list()))
                    char_util.set_init()
                    await append_character_card.finish(f"角色卡 {file_name} 已保存！")
                except Exception as e: # Catch potential exceptions during file processing
                    await append_character_card.finish(f"角色卡处理失败，错误信息: {e}")
            else:
                await append_character_card.finish("未能获取文件下载链接或文件名。")
        return # Exit after processing image segment


@append_character_card.got("message", prompt="请上传角色卡文件 (图片或 JSON)") # Improved prompt
async def update_file(event: MessageEvent):
    script_dir = os.path.dirname(__file__)
    message = event.get_message()

    for part in message:
        file_id = None
        file_name = None
        file_type = None
        image_url = None

        if part.type == "image":
            image_url = part.data["url"]
            file_id = part.data["file_id"]
        elif part.type == "file":
            file_id = part.data["file_id"]

        if file_id: # Proceed only if file_id is available
            file_name_with_ext = file_id.split('.')[-2].lower() + "." + file_id.split('.')[-1].lower() # Reconstruct filename with ext
            file_name = file_id.split('.')[-2].lower() # Filename without ext
            file_type = file_id.split('.')[-1].lower()

            try:
                source_path = await get_file(file_id) # Get file path here to avoid repeated calls
                if file_type == "png":
                    character_card_parser = CharacterCardParser()
                    img_path = await character_card_parser.download_file(image_url, file_name_with_ext) # Use reconstructed filename
                    character_card_parser.extract_character_card(img_path)
                    await append_character_card.send(str(char_util.get_character_card_list()))
                    char_util.set_init()
                    await append_character_card.finish("角色卡 (PNG) 已添加！")
                elif file_type == "json":
                    destination_path = os.path.join(script_dir, "./data/character_cards/json", f"{file_name}.{file_type}")
                    with open(source_path, 'rb') as src, open(destination_path, 'wb') as dst:
                        dst.write(src.read())
                    await append_character_card.send(str(char_util.get_character_card_list()))
                    char_util.set_init()
                    await append_character_card.finish("角色卡 (JSON) 已添加！")
                else:
                    await append_character_card.finish(f"不支持的文件类型: {file_type}, 请上传 PNG 或 JSON 文件。")
               #return # Exit after successful file processing

            except json.JSONDecodeError:
                await append_character_card.finish("收到的文件不是有效的 JSON 文件。")
            except Exception as e: # Catch other potential exceptions
                await append_character_card.finish(f"文件处理失败，错误信息: {e}")

    await append_character_card.finish("未检测到有效的文件或图片。") # Fallback message


# 获取文件
async def get_file(file_id: str):
    url = "http://127.0.0.1:3000/get_file" # Corrected URL - removed extra space
    payload = json.dumps({"file_id": file_id})
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10) # Using POST and timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()['data']
        source_path = data['url']
        return source_path
    except requests.exceptions.RequestException as e: # Catch request exceptions
        raise Exception(f"获取文件失败: {e}") # Re-raise with more context


# 设置聊天服务来源
set_proxy_type = on_command("设置聊天服务来源", permission=SUPERUSER, priority=5, block=True) # Added priority and block
chat_completion_type = ["OpenAI", "Claude", "Google AI Studio", "DeepSeek", "Others"]
@set_proxy_type.handle()
async def handle_proxy_type(event: MessageEvent, args: Message = CommandArg()):
    proxy_type = args.extract_plain_text().strip()
    if proxy_type in chat_completion_type:
        open_ai.set_chat_completion_source(proxy_type)
        await set_proxy_type.finish(f"已设置文本补全类型为：{proxy_type}")
    else:
        await set_proxy_type.send(f"无效的文本补全类型，请选择以下之一：{', '.join(chat_completion_type)}")


# 设置代理url
set_api_url = on_command("设置代理url", permission=SUPERUSER, priority=5, block=True) # Added priority and block
@set_api_url.handle()
async def handle_api_url(event: MessageEvent, api_url: Message = CommandArg()):
    api_url_str = api_url.extract_plain_text().strip()
    if api_url_str:
        open_ai.set_api_url(api_url_str)
        await set_api_url.finish(f"已设置代理url为：{api_url_str}")
    else:
        await set_api_url.send("请输入有效的代理url！")


# 设置代理密钥
set_api_key = on_command("设置代理密钥", permission=SUPERUSER, priority=5, block=True) # Added priority and block
@set_api_key.handle()
async def handle_api_key(event: MessageEvent, args: Message = CommandArg()):
    api_key_str = args.extract_plain_text().strip()
    if api_key_str:
        open_ai.set_api_key(api_key_str)
        await set_api_key.finish(f"已设置代理密钥为：{api_key_str}")
    else:
        await set_api_key.send("请输入有效的代理密钥！")


# 设置模型
set_chat_module = on_command("设置模型", permission=SUPERUSER, priority=5, block=True) # Added priority and block
@set_chat_module.handle()
async def handle_module(event: MessageEvent, args: Message = CommandArg()):
    module_name = args.extract_plain_text().strip()
    if module_name:
        open_ai.set_module(module_name)
        await set_chat_module.finish(f"已设置模型为：{module_name}")
    else:
        await set_chat_module.send(f"无效的模型名称，请重新设置")


# 设置max_tokens
set_max_tokens = on_command("设置max_tokens", permission=SUPERUSER, priority=5, block=True) # Added priority and block
@set_max_tokens.handle()
async def handle_max_token(event: MessageEvent, args: Message = CommandArg()):
    max_tokens_text = args.extract_plain_text().strip()
    if max_tokens_text.isdigit() and int(max_tokens_text) > 0:
        max_tokens = int(max_tokens_text)
        open_ai.set_max_tokens(max_tokens)
        await set_max_tokens.finish(f"已设置最大令牌数为：{max_tokens}")
    else:
        await set_max_tokens.send("请输入有效的正整数！")


# 设置temperature
set_temperature = on_command("设置temperature", permission=SUPERUSER, priority=5, block=True) # Added priority and block
@set_temperature.handle()
async def handle_temperature(event: MessageEvent, args: Message = CommandArg()):
    temperature_text = args.extract_plain_text().strip()
    try:
        temperature = float(temperature_text)
        if 0 < temperature < 2: # Corrected range check
            open_ai.set_temperature(temperature)
            await set_temperature.finish(f"已设置温度为：{temperature}")
        else:
            await set_temperature.send("请输入0到2之间的浮点数") # More specific message
    except ValueError:
        await set_temperature.send("无效的温度值，请输入有效的数字！") # More specific message


# 上传预设文件
upload_preset_file = on_command("上传预设", priority=5, block=True) # Added priority and block
@upload_preset_file.handle()
async def upload_preset(event: MessageEvent, args: Message = CommandArg()):
    await upload_preset_file.send("请上传预设 JSON 文件") # Improved initial message


@upload_preset_file.got(key="message")
async def upload_preset_handler(event: MessageEvent): # Renamed handler for clarity
    script_dir = os.path.dirname(__file__)
    message = event.get_message()

    for part in message:
        if part.type == "file":
            file_id = part.data["file_id"]
            file_name = str(part.data["file"]).strip(".json") # Get filename from data["file"]
            file_type = file_id.split('.')[-1].lower()

            if file_type == "json":
                try:
                    source_path = await get_file(file_id)
                    destination_path = os.path.join(script_dir, ".config/preset/ST_preset", f"{file_name}.{file_type}")

                    sillytavern_preset = SillyTavernPreset(source_path)
                    sillytavern_preset.save_preset(file_name, file_type)
                    prompt_order_path = os.path.join(script_dir, f'./config/preset/preset_prompt_orders/{file_name}')
                    os.makedirs(prompt_order_path, exist_ok=True) # Use makedirs with exist_ok
                    with open(os.path.join(prompt_order_path, 'private_prompt_order.json'), 'w', encoding='utf-8') as f:
                        order = {"order": sillytavern_preset.get_prompt_order().get(100001, {})} # Use .get() for safety
                        json.dump(order, f, indent=4, ensure_ascii=False)

                    await upload_preset_file.finish("预设上传成功！") # Improved success message

                except json.JSONDecodeError:
                    await upload_preset_file.finish("上传失败：无效的 JSON 文件。") # Improved error message
                except Exception as e: # Catch other potential exceptions
                    await upload_preset_file.finish(f"预设上传失败，错误信息: {e}") # Improved error message
            return # Exit after processing json

    await upload_preset_file.finish("上传失败：请上传 JSON 预设文件。") # Improved error message if no json found


# 查看预设列表
check_preset_list = on_command("查看预设列表", priority=5, block=True) # Added priority and block
@check_preset_list.handle()
async def get_preset_list(event: MessageEvent):
    preset_list = PresetManage.get_preset_list()
    output = "预设列表:\n" # Added header
    if preset_list:
        output += "\n".join(preset_list) # More efficient string join
    else:
        output += "当前没有预设。" # Message for empty list
    await check_preset_list.finish(output)


# 设置预设
set_preset = on_command("设置预设", priority=5, block=True) # Added priority and block
@set_preset.handle()
async def set_Preset(event: MessageEvent, args: Message = CommandArg()):
    message_type = event.message_type
    preset_name = args.extract_plain_text().strip()
    script_dir = os.path.dirname(__file__)
    preset_config_path = os.path.join(script_dir, './config/preset/preset_config/preset_config.json')

    try:
        with open(preset_config_path, 'r+', encoding='utf-8') as rf: # Use r+ mode
            preset_config: dict = json.load(rf)
    except (FileNotFoundError, json.JSONDecodeError): # Handle file not found or json error
        preset_config = {"group": {}, "private": {}} # Initialize if file doesn't exist or is invalid

    if message_type == "group":
        chat_user_id = str(event.group_id)
    else:
        chat_user_id = str(event.user_id)

    if preset_name not in PresetManage.get_preset_list(): # Validate preset name
        await set_preset.finish("预设不存在，请先上传预设或查看预设列表。") # Improved message

    preset_config.setdefault(message_type, {})[chat_user_id] = preset_name # Use setdefault for safety

    with open(preset_config_path, 'w', encoding='utf-8') as wf: # Use 'w' mode for writing
        json.dump(preset_config, wf, indent=4, ensure_ascii=False)

    if message_type == "group":
        chat_session: ChatSession = chat_util.get_group_session(chat_user_id)
    else:
        chat_session = chat_util.get_private_session(chat_user_id)

    if chat_session: # Check if session exists before setting preset
        chat_session.set_preset_order_prompts(chat_util.preset_manage.get_order_prompts(message_type, chat_user_id))
        chat_session.preset_name = chat_util.preset_manage.get_preset_name(message_type, chat_user_id)

    await set_preset.finish(f"已设置预设为：{preset_name}")