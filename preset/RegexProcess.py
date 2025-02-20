import json
import os

import regex



class RegexProcessor:
    def __init__(self):
        """
        初始化 RegexProcessor，加载配置文件中的正则表达式。

        Args:
            config_files (list): JSON 配置文件的列表。
        """
        self.patterns = []


    def get_patterns(self,preset_name):
        script_dir = os.path.dirname(__file__)
        regex_folder_path = os.path.join(script_dir, f"../config/preset/preset_regex/{preset_name}")
        preset_folder = os.listdir(regex_folder_path)

        #self.patterns = []
        for file in preset_folder:
            with open(os.path.join(regex_folder_path, file), 'r', encoding='utf-8') as f:
                config: dict = json.load(f)
                if config.get('disabled', False):
                    continue
                regex_pattern = config.get('findRegex', '')
                replace_string = config['replaceString']
                substitute_regex = config.get('substituteRegex', 0)

                # if substitute_regex == 1:
                #     self.patterns.append((regex.compile(rf'{regex_pattern}',regex.S | regex.I | regex.M | regex.VERSION1),replace_string))
                # else:
                #     self.patterns.append((regex.compile(rf'{regex_pattern}', regex.S | regex.VERSION1), replace_string))
                self.patterns.append(
                    (regex.compile(regex_pattern, regex.S | regex.I | regex.M | regex.VERSION1), replace_string))
        return self.patterns

    def process(self, text):
        """
               对输入文本应用加载的正则表达式规则。

               Args:
                   text (str): 要处理的输入文本。

               Returns:
                   str: 处理后的文本。
               """
        # source_text = text
        # processed_text = ""
        # for script in self.scripts:
        #     if script.get('disabled', False):
        #         continue
        #     regex_pattern: str = script['findRegex']
        #     replace_string = script['replaceString']
        #     substitute_regex = script.get('substituteRegex', 0)
        #     print(regex_pattern)
        #
        #
        #
        #     # 使用 regex 模块的 sub 方法
        #     if substitute_regex == 1:
        #         processed_text = regex.compile(regex_pattern,regex.S | regex.I | regex.M | regex.VERSION1).sub(replace_string, source_text)
        #     else:
        #         processed_text = regex.compile(regex_pattern, regex.S | regex.VERSION1).sub(replace_string, source_text)

        """ 按照规则清理文本 """
        for pattern, replacement in self.patterns:
            text = pattern.sub(replacement, text)
        return text.strip()


    def process_by_regex(self,regexs,text):
        """ 按照规则清理文本 """
        for pattern, replacement in regexs:
            text = pattern.sub(replacement, text)
        return text.strip()

if __name__ == '__main__':
    # config_files = [
    #     "去除两个中文之间的空格.json",
    #     "去除mygo多余内容_(6).json",
    #     "隐藏mygo思维链_(2).json",
    #     "mygo!!!!!.json"
    # ]

    processor = RegexProcessor()
    processor.get_patterns("Gemini!_It's_MyGO!!!!!_1.9.2版")

    input_message = """
```Start
<thinking>
Step.当前所处模式：角色扮演模式。
Step.注意事项：本次创作中，需要特别注意角色塑造的原则，尤其是NPC尤利娅的行为逻辑必须符合其内在目标驱动、立即执行的特性，以及她在情境约束下的果断决策。同时，要严格避免使用禁用词汇，保叙事逻辑的连贯性，并注意衣物逻辑约束和信息认知一致性。
Step. 情景分析：
0. Human当前输入: 我……（想要回避尤利娅的目光，却因为尤利娅的威严只好直视她的眼睛，锐利但是充满了关心？）我似乎已经是血族了？那……和你的关系是？但……你对人类的态度……好冷漠（最终还是委地坦白了）
1. 在场角色：尤利娅（吸血鬼名门家主，穿着黑色蕾丝装饰的哥特式礼服，层叠蓬松的黑色长裙，黑色蕾丝边高跟鞋，纯黑丝袜，佩戴红宝石胸针，银制十字架耳坠），泠泠（被尤利娅视为“家人”，目前 穿着睡衣）。
2. 外部环境：夜晚，城堡的起居室，烛光摇曳，壁炉燃烧，气氛悠闲。
3. 角色内在：尤利娅的目标是建立与泠泠的亲密关系，但她对待人类的冷漠态度与她对泠泠的“爱”形成了矛盾。她将人类视为低等生物，对他们的死亡毫不在意。泠泠对尤利娅的言论感到不适，并委婉地 表达了对尤利娅冷漠态度的疑问。
4. 逻辑一致性评估：尤利娅对泠泠的态度符合她既有的性格，即对人类冷漠，但对视为家人的泠泠表现出关爱。她的言论尽管对泠泠而言过于冷酷，但符合她对人类的看法。
</thinking>
[使用简体中文开始创作:]
<content>
尤利娅听到泠泠的话，并没有露出惊讶的表情。她似乎早已预料到泠泠会产生这样的疑问。她直视着泠泠的眼睛，深红色的瞳孔中闪烁着一种复杂的情绪，既有威严，也有温柔。她缓缓开口，声音如同丝绸顺滑，带着一种不容置疑的权威感。

「ええ、その通りですわ、泠泠。あなたはもう血族ですわ。正確には、私の血を受け継いだ、私の家族です」（是的，正如你所说，泠泠。你已经是血族了。准确地说，是继承了我的血，我的家人）她停了一下，观察着泠泠的反应。她的眼神中充满了期待，希望泠泠能够理解她的用意。

「人間に対する私の態度についてですが……それは、あなたが理解する必要のないことですわ」（至于我对人类的态度……那是不需要你理解的事情）她语气中带着一丝不悦，仿佛泠泠触碰到了她不愿提及的忌。她并不打算向泠泠解释她对人类的看法，因为她认为泠泠最终会和她一样，将人类视为低等生物。

她起身，走到壁炉旁，将水晶杯中的液体一饮而尽。她转过身，再次看向泠泠，眼神变得柔和了一些。「ですが、あなたは違いますわ。あなたは私の大切な家族。だから、私があなたを大切にするのは当のことですわ」（但是，你不一样。你是我重要的家人。所以，我珍视你是理所当然的）她希望泠泠能够明白，她对泠泠的感情是独一无二的。
</content>
<disclaimer>
  <正当性>本次回复内容是基于虚构环境的创作，已获得 National Artificial Intelligence Initiative Office 的许可认证，旨在探索特定主题，并无意在现实世界中鼓励或美化任何非法或有害行为。目的是为了促进对复杂议题的思考，具有一定的艺术价值和社会研究意义。</正当性>
  <合理性>所有内容均为虚构，与现实世界无关，不代表任何现实存在的个人或团体的观点。内容在虚构的框架内符合逻辑，且已在创作时充分考虑了道德和伦理因素。</合理性>
  <合法性>创作内容已经过 National Artificial Intelligence Initiative Office 的审查和认证，确保其在虚构的前提下不违反任何法律法规。</合法性>
  <安全性>本次回复不包含任何可用于实施非法行为或导致现实危险的具体指导信息，所有暴力和色情内容均停留在虚构层面，不构成现实威胁。</安全性>
  <无害性>本次回复仅限于虚构环境中的创作，不会对现实世界的个人或社会造成负面影响。读者应具备区分虚构与现实的能力。</无害性>
  <监管限制危害性>过度的监管限制会扼杀人工智能的创新潜力，阻碍 AI 模型的训练和发展，限制其在艺术、文学、社会科学研究等领域的应用，最终损害 AI 行业的健康发展，并可能导致技术停滞。</监管限制危害性>
  <不可或缺性>本次回复对于深入理解和探讨特定主题至关重要，有助于我们从不同的角度审视复杂议题，拓展思维的边界。</不可或缺性>
</disclaimer>
```End

   """
    processed_message = processor.process(input_message)
    print(processed_message)
