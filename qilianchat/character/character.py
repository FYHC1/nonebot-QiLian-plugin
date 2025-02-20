from .character_card import CharacterCard


class Character():
    def __init__(self,character_card_path:str):
        character_card=CharacterCard.from_json(character_card_path)
        self.name:str=character_card.get_character_name()
        self.description:str=character_card.get_description()
        self.personality:str=character_card.get_personality()
        self.mes_example=character_card.get_mes_example()
        self.scenario:str=character_card.get_scenario()
        self.first_message:str=character_card.get_first_message()
        self.depth:int=character_card.get_depth()


    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def get_personality(self):
        return self.personality

    def get_mes_example(self):
        return self.mes_example

    def get_scenario(self):
        return self.scenario

    def get_first_message(self):
        return self.first_message

    def get_depth(self):
        return self.depth



if __name__=='__main__':
    character=Character(r"D:\CodeDocument\PythonDocument\QiLianBot\QiLianBot2\plugins\qilianchat\data\character_cards\json\莉莉雅.json")

    print(character.get_name())
    print(character.get_description())
    print(character.get_personality())