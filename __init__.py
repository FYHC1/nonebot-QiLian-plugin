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
from requests import session

from .character.character_card_parser import CharacterCardParser
from .chat.chat import Chat
from .chat.chat_session import ChatSession
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="QiLianChat",
    description="基于大语言模型的角色扮演聊天插件",
    usage="使用 '怜祈 帮助' 查看详细使用说明",
    config=Config,
)

from .messages.messages import Messages
from .open_ai.open_ai import OpenAi
from .preset.RegexProcess import RegexProcessor
from .preset.preset_convert import SillyTavernPreset
from .preset.QLPreset_manage import QLPresetManager

from .util.character_util import CharacterUtil
from .chat.chat_session_manager import ChatSessionManager

#实例对象
char_util=CharacterUtil()
chat=Chat()
chat_util=ChatSessionManager()
messages=Messages()
regex_process=RegexProcessor()
open_ai=OpenAi()
character_list=char_util.get_character_card_list()


tigger=on_startswith(("怜祈"),ignorecase=True)
@tigger.handle()
async def lian_qi():
   await tigger.finish("正在运行中")


help_command = on_command("怜祈 帮助", priority=1, block=True)
@help_command.handle()
async def handle_help():
    help_message = """怜祈 插件帮助

**触发关键词:**
- 怜祈 (保持插件运行)

**角色管理 (Superuser权限):**
- 查看角色列表: 查看当前已加载的角色卡列表。
- 指定聊天角色 <角色名>:  指定当前群聊/私聊的角色。
- 上传角色卡 (回复图片消息): 上传角色卡图片以添加新角色。
- 上传角色卡 (发送命令后上传图片/json文件):  上传角色卡图片或JSON文件以添加新角色。

**预设管理 (Superuser权限):**
- 查看预设列表: 查看当前已加载的预设列表。
- 上传预设 (回复json文件消息): 上传 SillyTavern 预设 JSON 文件。
- 上传预设 (发送命令后上传json文件): 上传 SillyTavern 预设 JSON 文件。
- 设置预设 <预设名>: 设置当前群聊/私聊使用的预设。

**聊天管理 (Superuser权限):**
- clear: 清空当前群聊/私聊的角色聊天记忆。

**OpenAI/模型设置 (Superuser权限):**
- 设置聊天服务来源 <来源类型>: 设置文本补全服务来源，可选: OpenAI, Claude, Google AI Studio, DeepSeek, Others。
- 设置代理url <URL>: 设置API代理URL。
- 设置代理密钥 <密钥>: 设置API密钥。
- 设置模型 <模型名称>: 设置使用的模型名称。
- 设置max_tokens <正整数>: 设置模型生成回复的最大令牌数。
- 设置temperature <0~2浮点数>: 设置模型temperature参数，影响生成回复的随机性。

**聊天互动:**
- 在群聊中 @Bot + 消息内容 即可进行角色扮演对话。
- 在私聊中 直接发送消息内容 即可进行角色扮演对话。
"""
    await help_command.finish(help_message)


#查看角色列表
check_characters=on_command("查看角色列表")
@check_characters.handle()
async def check_characters_list():
    character_list=char_util.get_character_card_list()
    await check_characters.finish(str(character_list))


#指定聊天角色
appoint_character=on_command("指定聊天角色")
@appoint_character.handle()
async def appoint_chat_character(event:MessageEvent,args:Message=CommandArg()):
    message_type = event.message_type
    character_name = args.extract_plain_text()
    chat_session_id=""
    if message_type == "group":
        chat_session_id = str(event.group_id)
    else:
        chat_session_id = str(event.user_id)

    if character_name not in character_list:
        appoint_character.finish("不存在此角色，请重新指定角色")
    await char_util.appoint_character(message_type,character_name,chat_session_id)
    await appoint_character.send(f"已指定聊天角色{character_name}")
    #await chat.new_chat()
    char_util.set_init()




def groupMessage(event:MessageEvent):
    message = event.get_plaintext()
    # 如果是群聊消息且不以/开头,则返回True
    return event.message_type=="group" and not message.startswith('/')

def privateMessage(event:MessageEvent):
    message = event.get_plaintext()
    # 如果是私聊消息且不以/开头,则返回True
    return event.message_type=="private" and not message.startswith('/')


role_play=on_message(rule=groupMessage & to_me(),priority=10,block=True)
@role_play.handle()
async def group_chat(event:MessageEvent,bot:Bot):
    message_type = event.message_type
    group_id=str(event.group_id)
    user_id=str(event.user_id)
    message=event.get_plaintext()
    chat_session = chat_util.get_session(message_type,group_id)
    if not chat_session:
        character=char_util.get_character_by_id(message_type,group_id)
        chat_util.preset_manage.set_preset_config(message_type, group_id, "Gemini!_It's_MyGO!!!!!_1.9.2版")
        chat_session = chat_util.create_session(message_type,character,group_id)
        chat_session.set_user_id(user_id)
        chat_session.set_preset_regex(regex_process.get_patterns(chat_session.preset_name))
        chat_util.set_group_session(group_id,chat_session)

    chat_session.set_nick_name(await chat_util.get_nick_name(bot, user_id))
    chat_history = await chat.get_context(message_type,group_id,chat_session.get_character_name())
    chat_messages = await messages.construct_messages(message,chat_session,chat_history)
    assistant_reply = await open_ai.start_chat(chat_messages)

    assistant_reply ="\n"+regex_process.process_by_regex(chat_session.get_preset_regex(),assistant_reply)
    await chat.save_chat_message(message_type,group_id,chat_session.get_nick_name(),chat_session.get_character_name(),message,assistant_reply)
    await role_play.finish(MessageSegment.at(user_id) + Message(assistant_reply))



role_play1=on_message(rule=privateMessage,priority=10,block=True)
@role_play1.handle()
async def private_chat(event:MessageEvent,bot:Bot):
    message_type = event.message_type
    #group_id = str(event.group_id)
    user_id = str(event.user_id)
    message = event.get_plaintext()
    chat_session = chat_util.get_session(message_type,user_id)
    if not chat_session:
        character = char_util.get_character_by_id(message_type, user_id)
        chat_util.preset_manage.set_preset_config(message_type, user_id, "Gemini!_It's_MyGO!!!!!_1.9.2版")
        chat_session = chat_util.create_session(message_type, character,user_id)
        chat_session.set_user_id(user_id)
        chat_session.set_preset_regex(regex_process.get_patterns(chat_session.preset_name))
        chat_util.set_private_session(user_id,chat_session)

    chat_session.set_nick_name(await chat_util.get_nick_name(bot, user_id))
    chat_history = await chat.get_context(message_type,user_id,chat_session.get_character_name())
    chat_messages = await messages.construct_messages(message, chat_session, chat_history)
    assistant_reply = await open_ai.start_chat(chat_messages)

    assistant_reply = "\n"+regex_process.process_by_regex(chat_session.get_preset_regex(), assistant_reply)
    await chat.save_chat_message(message_type,user_id,chat_session.get_nick_name(),chat_session.get_character_name(),message,assistant_reply)
    await role_play.finish(MessageSegment.at(user_id) + Message(assistant_reply))



#清空聊天记录
clear_chat=on_command("clear",permission=SUPERUSER)
@clear_chat.handle()
async def clear_chat_message(event:MessageEvent):
    message_type=event.message_type
    if message_type=="group":
        chat_user_id=str(event.group_id)
    else:
        chat_user_id=str(event.user_id)

    character_name=char_util.get_character_name(message_type,chat_user_id)
    print(message_type, chat_user_id,character_name)
    await chat.clear_chat_message(message_type,chat_user_id,character_name)
    await clear_chat.finish("记忆已清除...")



#添加角色卡
append_character_card=on_command("上传角色卡",permission=SUPERUSER)
@append_character_card.handle()
async def handle_file(event: MessageEvent,bot:Bot):
    # 检查消息是否包含文件
    character_card_paser=CharacterCardParser()
    print(event.message)
    for segment in event.message:
        if segment.type == "image":
            # 获取图片的 URL
            image_url = segment.data["url"]
            parsed_url = urlparse(image_url)
            query_params = parse_qs(parsed_url.query)  # 解析查询参数
            file_name =query_params.get("fileid", [None])[0]
            # print(image_url,file_name)
            if image_url:
                # 下载文件并保存
                img_path= await character_card_paser.download_file(image_url, file_name)
                character_card_paser.extract_character_card(img_path)
                await append_character_card.send(str(char_util.get_character_card_list()))
                char_util.set_init()
                await append_character_card.finish(f"文件 {file_name} 已保存！")
            else:
                await append_character_card.finish("未能获取文件下载链接。")


@append_character_card.got("message",prompt="请上传文件")
async def update_file(event:MessageEvent):
    global file_type, file_id, file_name, image_url
    script_dir = os.path.dirname(__file__)
    message = event.get_message()

    for part in message:
        if part.type == "image":
            # 处理图片文件
            image_url = part.data["url"]
            file_id = part.data["file_id"]
            file_name = file_id.split('.')[-2].lower()
            file_type = file_id.split('.')[-1].lower()
        elif part.type == "file":
            file_id=part.data["file_id"]
            file_name = file_id.split('.')[-2].lower()
            file_type = file_id.split('.')[-1].lower()  # 获取文件扩展名
        if file_type == "png":
            character_card_paser=CharacterCardParser()
            img_path= await character_card_paser.download_file(image_url, file_name)
            character_card_paser.extract_character_card(img_path)
            await append_character_card.send(char_util.get_character_list())
            char_util.set_init()
            await append_character_card.finish("收到PNG数据")
        elif file_type == "json":
            source_path = await get_file(file_id)
            destination_path=os.path.join(script_dir,"./data/character_cards/json",f"{file_name}.{file_type}")
            # 处理 JSON 文件
            try:
                with open(source_path, 'rb') as src, open(destination_path, 'wb') as dst:
                    dst.write(src.read())

                #await init()
                await append_character_card.send(char_util.get_character_list())

                await append_character_card.finish(f"收到 JSON 数据")
            except json.JSONDecodeError:
                await append_character_card.finish("收到的文件不是有效的 JSON 文件。")
        else:
            # 处理其他文件类型
            await append_character_card.finish(f"收到一个文件：{file_name}.{file_type}")
    # else:
    #     await append_character_card.finish("收到的消息中没有包含有效的文件。")


# 获取文件
async def get_file(file_id: str):
    url = " http://127.0.0.1:3000/get_file"
    payload = json.dumps({
        "file_id": file_id
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()['data']
    source_path = data['url']
    #print(source_path)
    '''
        {"status":"ok","retcode":0,"data":{"file":"C:\\Users\\hgl\\Documents\\Tencent Files\\NapCat\\temp\\怜祈.json","url":"C:\\Users\\hgl\\Documents\\Tencent Files\\NapCat\\temp\\怜祈.json","file_size":"1197","file_name":"怜祈.json"},"message":"","wording":"","echo":null}

    '''
    return source_path



set_proxy_type = on_command("设置聊天服务来源",permission=SUPERUSER)
chat_completion_type = ["OpenAI", "Claude", "Google AI Studio","DeepSeek","Others"]
@set_proxy_type.handle()
async def handle_proxy_type(event: MessageEvent, args: Message = CommandArg()):
    proxy_type = args.extract_plain_text()
    if proxy_type in chat_completion_type:
        open_ai.set_chat_completion_source(proxy_type)
        await set_proxy_type.finish(f"已设置文本补全类型为：{proxy_type}")
    else:
        await set_proxy_type.send(f"无效的文本补全类型，请选择以下之一：{', '.join(chat_completion_type)}")

@set_proxy_type.got("chat_type", prompt=f"请输入文本补全类型：{', '.join(chat_completion_type)}")
async def handle_proxy_type_followup(event: MessageEvent):
    chat_type = event.get_plaintext()
    if chat_type in chat_completion_type:
        open_ai.set_chat_completion_source(chat_type)
        await set_proxy_type.finish(f"已设置文本补全类型为：{chat_type}")
    else:
        await set_proxy_type.finish(f"无效的文本补全类型，请选择以下之一：{', '.join(chat_completion_type)}")


set_api_url = on_command("设置代理url",permission=SUPERUSER)
@set_api_url.handle()
async def handle_api_url(event: MessageEvent, api_url: Message = CommandArg()):
    api_url = api_url.extract_plain_text().strip()
    if api_url:
        open_ai.set_api_url(api_url)
        await set_api_url.finish(f"已设置代理url为：{api_url}")
    else:
        await set_api_url.send("请输入有效的代理url！")

@set_api_url.got("api_url", prompt="请输入代理url")
async def handle_api_url_followup(event: MessageEvent):
    api_url = event.get_plaintext().strip()
    if api_url:
        open_ai.set_api_url(api_url)
        await set_api_url.finish(f"已设置代理url为：{api_url}")
    else:
        await set_api_url.finish("无效的代理url，请重新输入！")




set_api_key = on_command("设置代理密钥",permission=SUPERUSER)
@set_api_key.handle()
async def handle_api_key(event: MessageEvent, args: Message = CommandArg()):
    key = args.extract_plain_text().strip()
    if key:
        open_ai.set_api_key(key)
        await set_api_key.finish(f"已设置代理密钥为：{key}")
    else:
        await set_api_key.send("请输入有效的代理密钥！")

@set_api_key.got("key", prompt="请输入代理密钥")
async def handle_api_key_followup(event: MessageEvent):
    key = event.get_plaintext().strip()
    if key:
        open_ai.set_api_key(key)
        await set_api_key.finish(f"已设置代理密钥为：{key}")
    else:
        await set_api_key.finish("无效的代理密钥，请重新输入！")


set_chat_module = on_command("设置模型",permission=SUPERUSER)
#module_name = ["gpt-4o","gpt-4o-mini","gpt-4","gpt-4 turbo","gpt-3.5","gpt-3.5 turbo"]
@set_chat_module.handle()
async def handle_module(event: MessageEvent, args: Message = CommandArg()):
    module = args.extract_plain_text().strip()
    if module:
        open_ai.set_module(module)
        await set_chat_module.finish(f"已设置模型为：{module}")
    else:
        await set_chat_module.send(f"无效的模型名称，请重新设置")

@set_chat_module.got("module", prompt=f"请输入模型名称\n")
async def handle_module_followup(event: MessageEvent):
    module = event.get_plaintext().strip()
    if module:
        open_ai.set_module(module)
        await set_chat_module.finish(f"已设置模型为：{module}")
    else:
        await set_chat_module.finish(f"无效的模型名称，请重新设置")


set_max_tokens = on_command("设置max_tokens",permission=SUPERUSER)
@set_max_tokens.handle()
async def handle_max_token(event: MessageEvent, args: Message = CommandArg()):
    max_tokens_text = args.extract_plain_text().strip()
    if max_tokens_text.isdigit() and int(max_tokens_text) > 0:
        max_tokens = int(max_tokens_text)
        open_ai.set_max_tokens(max_tokens)
        await set_max_tokens.finish(f"已设置最大令牌数为：{max_tokens}")
    else:
        await set_max_tokens.send("请输入有效的正整数！")

@set_max_tokens.got("max_tokens", prompt="请输入max_tokens")
async def handle_max_token_followup(event: MessageEvent):
    max_tokens_text = event.get_plaintext().strip()
    try:
        max_tokens = int(max_tokens_text)
        if max_tokens > 0:
            open_ai.set_max_tokens(max_tokens)
            await set_max_tokens.finish(f"已设置最大令牌数为：{max_tokens}")
        else:
            await set_max_tokens.finish("令牌数必须是正整数！")
    except ValueError:
        await set_max_tokens.finish("无效的令牌数，请输入一个正整数！")


set_temperature = on_command("设置temperature",permission=SUPERUSER)
@set_temperature.handle()
async def handle_temperature(event: MessageEvent, args: Message = CommandArg()):
    temperature_text = args.extract_plain_text().strip()
    try:
        temperature = float(temperature_text)
        if temperature>0 and temperature<2:
            open_ai.set_temperature(temperature)
        else:
            await set_temperature.send("请输入0到2的浮点数")
        await set_temperature.finish(f"已设置温度为：{temperature}")
    except ValueError:
        await set_temperature.send("请输入有效的温度值！")

@set_temperature.got("temperature", prompt="请输入temperature")
async def handle_temperature_followup(event: MessageEvent):
    temperature_text = event.get_plaintext().strip()
    try:
        temperature = float(temperature_text)
        if temperature>0 and temperature<2:
            open_ai.set_temperature(temperature)
        else:
            await set_temperature.finish("请输入0到2的浮点数")

        await set_temperature.finish(f"已设置温度为：{temperature}")
    except ValueError:
        await set_temperature.finish("无效的温度值，请重新输入！")


upload_preset_file=on_command("上传预设")
@ upload_preset_file.handle()
async def upload_preset(event: MessageEvent, args: Message = CommandArg()):
    global file_id, file_name, file_type
    script_dir = os.path.dirname(__file__)
    message = event.get_message()

    for part in message:
        if part.type == "file":
            file_id = part.data["file_id"]
            file_name = file_id.split('.')[-2].lower()
            file_type = file_id.split('.')[-1].lower()
        if part.type == "json":
            source_path = await get_file(file_id)
            destination_path = os.path.join(script_dir, ".config/preset/ST_preset", f"{file_name}.{file_type}")

            try:
                sillytavern_preset = SillyTavernPreset(source_path)
                sillytavern_preset.save_preset(file_name, file_type)
                propmt_order_path = os.path.join(script_dir, f'./config/preset/preset_prompt_orders/{file_name}')
                if not os.path.exists(propmt_order_path):
                    os.mkdir(os.path.join(propmt_order_path))
                    order = {"order": sillytavern_preset.get_prompt_order()["100001"]}
                    sillytavern_preset.save_prompt_order("private", file_name, order)
                    sillytavern_preset.save_prompt_order("group", file_name, order)

                await upload_preset_file.send("已上传预设")
            except json.JSONDecodeError:
                await upload_preset_file.finish("收到的文件不是有效的 JSON 文件。")
        else:
            # 处理其他文件类型
            await upload_preset_file.send(f"请上传json文件")

@upload_preset_file.got(key="message",prompt="请上传预设")
async def upload_preset(event: MessageEvent):
    global file_id,file_name,file_type
    script_dir = os.path.dirname(__file__)
    message = event.get_message()

    for part in message:
        if part.type == "file":
            file_id = part.data["file_id"]
            file_name = str(part.data["file"]).strip(".json")
            file_type = file_id.split('.')[-1].lower()
            #print(file_id, file_name, file_type)
        if file_type == "json":
            source_path = await get_file(file_id)
            destination_path = os.path.join(script_dir, ".config/preset/ST_preset", f"{file_name}.{file_type}")

            #print("trigger")
            try:
                sillytavern_preset = SillyTavernPreset(source_path)
                sillytavern_preset.save_preset(file_name,file_type)
                propmt_order_path=os.path.join(script_dir,f'./config/preset/preset_prompt_orders/{file_name}')
                if not os.path.exists(propmt_order_path):
                    os.mkdir(os.path.join(propmt_order_path))
                # with open(os.path.join(script_dir,f'./config/preset/preset_prompt_orders/{file_name}/private_prompt_order.json'),'w',encoding='utf-8') as f:
                #     order={"order":sillytavern_preset.get_prompt_order()["100001"]}
                #     json.dump(order,f,indent=4,ensure_ascii=False)
                    order = {"order": sillytavern_preset.get_prompt_order()["100001"]}
                    sillytavern_preset.save_prompt_order("private",file_name,order)
                    sillytavern_preset.save_prompt_order("group",file_name,order)

                #await upload_preset_file.send(private_prompt_manage.get_preset_list())
                await upload_preset_file.send("已上传预设")
            except json.JSONDecodeError:
                await upload_preset_file.finish("收到的文件不是有效的 JSON 文件。")
        else:
            # 处理其他文件类型
            await upload_preset_file.finish(f"收到一个文件：{file_name}.{file_type}")


check_preset_list=on_command("查看预设列表")
@check_preset_list.handle()
async def get_preset_list(event: MessageEvent):
    preset_list=QLPresetManager.get_preset_list()
    output=""
    for preset in preset_list:
        output += f"{preset}\n"
    await check_preset_list.finish(output)



set_preset=on_command("设置预设")
@set_preset.handle()
async def set_Preset(event: MessageEvent,args: Message = CommandArg()):
    message_type=event.message_type
    preset_name=args.extract_plain_text().strip()
    script_dir = os.path.dirname(__file__)
    preset_config_path=os.path.join(script_dir,f'./config/preset/preset_config/preset_config.json')
    with open(preset_config_path,'r+',encoding='utf-8') as rf:
        preset_config:dict =json.load(rf)
    with open(preset_config_path,'w+',encoding='utf-8') as wf:
        if message_type=="group":
            session_id=str(event.group_id)
        else:
            session_id=str(event.user_id)
        preset_config[message_type][session_id] = preset_name
        json.dump(preset_config, wf, indent=4, ensure_ascii=False)
        chat_session=chat_util.get_session(message_type,session_id)
        chat_session.set_preset_order_prompts(chat_util.preset_manage.get_order_prompts(message_type, session_id))
        chat_session.preset_name = chat_util.preset_manage.get_preset_name(message_type, session_id)