import json
import os
from datetime import datetime


from nonebot.plugin import Plugin

from ..character.character import Character
#from ..user.user import User

# 设置聊天记录文件保存地址

script_dir = os.path.dirname(os.path.realpath(__file__))
group_chatmessage_path = os.path.join(script_dir, "../data/chat_data/group_chat")
private_chatmessage_path = os.path.join(script_dir, "../data/chat_data/private_chat")


class Chat:
    def __init__(self):
        self.message_type=''
        self.chat_user_id=''
        self.user_id=''
        self.character_name=''
        self.nickname=''
        self.message=''
        self.depth=8





    # def from_user(self,user:User):
    #     self.message_type = user.message_type
    #     self.chat_user_id = user.chat_user_id
    #     self.user_id = user.user_id
    #     self.character_name = user.character_name
    #     self.nickname = user.nickname
    #     self.message = user.message



    ###
    #
    #新建聊天记录
    async def new_chat(self,message_type,chat_user_id,character_name):
        files_list=[]
        relavative_path=""
        if message_type == "group":
            files_list=os.listdir(group_chatmessage_path)
            relavative_path = "../data/chat_data/group_chat"
        elif message_type == "private":
            files_list=os.listdir(private_chatmessage_path)
            relavative_path = "../data/chat_data/private_chat"
        if f"{message_type}-{chat_user_id}-{character_name}.jsonl" not in files_list:
            with open(os.path.join(script_dir, relavative_path,f"{message_type}-{chat_user_id}-{character_name}.jsonl"), 'w', encoding='utf-8') as f:
                print("创建新聊天")






    #保存聊天记录
    async def save_chat_message(self,message_type,chat_user_id,nickname,character_name,message,assistant_reply):
        files_list = []
        relavative_path = ""
        if message_type == "group":
            files_list = os.listdir(group_chatmessage_path)
            relavative_path = "../data/chat_data/group_chat"
        elif message_type == "private":
            files_list = os.listdir(private_chatmessage_path)
            relavative_path = "../data/chat_data/private_chat"
        if f"{message_type}-{chat_user_id}-{character_name}.jsonl" in files_list:
            with open(os.path.join(script_dir, relavative_path, f"{message_type}-{chat_user_id}-{character_name}.jsonl"),
                      'a+',encoding='utf-8') as f:
                chat_note = {}
                now = datetime.now()
                formatted_now = now.strftime("%Y-%m-%d@%H:%M:%S")
                chat_note["name"]=nickname
                chat_note["is_user"]=True
                chat_note["user_id"]=chat_user_id
                chat_note["is_system"]=False
                chat_note["msg"]=message
                chat_note["create_date"]=formatted_now
                f.write(json.dumps(chat_note,ensure_ascii=False)+'\n',)

                chat_note["name"]=character_name
                chat_note["is_user"] = False
                chat_note["user_id"] = chat_user_id
                chat_note["msg"] = assistant_reply
                chat_note["create_date"] = formatted_now
                f.write(json.dumps(chat_note,ensure_ascii=False)+'\n')





    #获取上下文
    async def get_context(self,message_type,chat_user_id,character_name):
        files_list = []
        context=[]
        relavative_path = ""
        depth=-self.depth

        if message_type == "group":
            files_list = os.listdir(group_chatmessage_path)
            relavative_path = "../data/chat_data/group_chat"
        elif message_type == "private":
            files_list = os.listdir(private_chatmessage_path)
            relavative_path = "../data/chat_data/private_chat"
        if f"{message_type}-{chat_user_id}-{character_name}.jsonl" in files_list:
            file_path=os.path.join(script_dir,relavative_path,f"{message_type}-{chat_user_id}-{character_name}.jsonl")
            if os.path.getsize(file_path) == 0:
                return context
            with open(file_path, 'r',encoding='utf-8') as f:
                lines = f.readlines()  # 将文件内容读取为列表
                for line in lines[depth:]:  # 使用切片操作
                    #print(line)
                    chat_note = json.loads(line)
                    #print(chat_note)
                    chat_message = {}
                    chat_message["name"] = chat_note["name"]
                    chat_message["is_user"] = chat_note["is_user"]
                    chat_message["msg"] = chat_note["msg"]
                    context.append(chat_message)

        else:
            await self.new_chat(message_type,chat_user_id,character_name)

        return context



    #清空聊天记录
    async def clear_chat_message(self,message_type,chat_user_id,character_name):

        relavative_path = f"../data/chat_data/{message_type}_chat"
        files_list=os.listdir(os.path.join(script_dir,relavative_path))

        if f"{message_type}-{chat_user_id}-{character_name}.jsonl" not in files_list:
            with open(os.path.join(script_dir, relavative_path,
                                   f"{message_type}-{chat_user_id}-{character_name}.jsonl"), 'w',
                      encoding='utf-8') as f:
                print("创建新聊天")

        else:
            with open(os.path.join(script_dir, relavative_path,
                                   f"{message_type}-{chat_user_id}-{character_name}.jsonl"), 'w',
                      encoding='utf-8') as f:
                print("聊天记录已清除~")


