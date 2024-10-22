"""
Author : Peter Kramar
Email : peter@ked.tech
This module contains the builder class for fm-gai-lottie-reading-v1 activity objects.
"""


import uuid
import random
from backend.helpers import initialize_activity_data
from backend.helpers import setup_logger
from backend.helpers import load_activity_blueprint_config
from backend.helpers import get_slot_weekday
from backend.helpers import make_activity_prompt
from backend.helpers import get_random_itoken
from backend.connectors import FmLottieConnector, CourseConnector, ITokenConnector


class FMGAILottieReadingActivityBlueprintBuilder:
    def __init__(self, activity):
        self.assignee = None
        self.activity = activity
        self.data = initialize_activity_data()
        self.activity_blueprint_config = load_activity_blueprint_config()
        self.logger = setup_logger()

    def set_id(self):
        self.activity.id = str(uuid.uuid4())
        self.logger.info(f"{self.__class__.__name__}: 'set_activity_id' method invoked - Activity ID set to: {self.activity.id}")
        return self
    
    def set_metadata(self):
        self.activity.metadata = {
            "analyst": self.activity_blueprint_config["metadata"].get("analyst"),
            "model_alias": self.activity_blueprint_config["metadata"].get("model_alias"),
            "model_version": self.activity_blueprint_config["metadata"].get("model_version"),
            "target_material": []
        }
        if self.activity_blueprint_config["metadata"].get("analyst") == "M-Maker25":
            self.assignee = "teacher1"
        if self.activity_blueprint_config["metadata"].get("analyst") == "CPTFreedom":
            self.assignee = "teacher2"
        self.logger.info(f"{self.__class__.__name__}: 'set_metadata' method invoked - Metadata set to: {self.activity.metadata}")
        return self

    def set_sandbox_slot_record(self):
        "Sets the sandbox slot record based on the activity blueprint configuration."
        course_connector = CourseConnector()
        if self.activity_blueprint_config["slot"] == "load_current_slot":
            self.activity.metadata["sandbox_slot"] = course_connector.get_current_slot_record(assignee=self.assignee)
        else:
            slot_date = self.activity_blueprint_config["slot"]["date"]
            group_alias = self.activity_blueprint_config["slot"]["group_alias"]
            slots = course_connector.get_slot_records_for_date(assignee=self.assignee, date=slot_date)
            for slot in slots:
                if slot["assigned_group"]["alias"] == group_alias:
                    self.activity.metadata["sandbox_slot"] = slot
        self.logger.info(f"{self.__class__.__name__}: 'set_sandbox_slot_record' method invoked - Sandbox slot record set to: {self.activity.metadata['sandbox_slot']}")
        return self
    
    def set_itokens(self):
        itoken_connector = ITokenConnector()
        students = self.activity.metadata["sandbox_slot"]["students"]
        for student in students:
            try:
                token = itoken_connector.get_token(student["alias"])
                self.activity.itokens = {}
                self.activity.itokens[student["alias"]] = token
            except Exception as e:
                self.logger.error(f"{self.__class__.__name__}: 'set_itokens' method invoked - Error: {e}")
                continue
        self.logger.info(f"{self.__class__.__name__}: 'set_itokens' method invoked - iTokens set to: {self.activity.itokens}")
        return self
    
    def set_cefr_level(self):
        course_connector = CourseConnector()
        self.activity.cefr_level = course_connector.get_cefr_level(course_id=self.activity.metadata["sandbox_slot"]["assigned_group"]["alias"])
        self.logger.info(f"{self.__class__.__name__}: 'set_cefr_level' method invoked - CEFR level set to: {self.activity.cefr_level}")
        return self
    
    def set_group_alias(self):
        self.activity.group_alias = self.activity.metadata["sandbox_slot"]["assigned_group"]["alias"]
        self.logger.info(f"{self.__class__.__name__}: 'set_group_alias' method invoked - Group alias set to: {self.activity.group_alias}")
        return self
    
    def set_target_vocabulary(self):
        print("set_target_vocabulary")
        target_vocabulary = []
        course_connector = CourseConnector()
        sandbox_slot = self.activity.metadata["sandbox_slot"]
        print("sandbox_slot", sandbox_slot)
        weekday = get_slot_weekday(sandbox_slot)
        course_id = sandbox_slot["assigned_group"]["alias"]
        print("course_id", course_id)
        print("self.assignee", self.assignee)
        print("weekday", weekday)
        words_dict = course_connector.get_target_vocabulary(course_id=course_id, assignee=self.assignee, weekday=str(weekday))
        print("words_dict", words_dict)
        for words in words_dict:
            words = words.get("words")
            print("words", words)
            for word in words:
                target_vocabulary.append(word)
        print("target_vocabulary", target_vocabulary)
        self.activity.target_vocabulary = target_vocabulary
        print("self.activity.target_vocabulary", self.activity.target_vocabulary)
        target_materials = course_connector.get_target_material(course_id=course_id, assignee=self.assignee, weekday=str(weekday))
        for material_record in target_materials:
            self.set_target_material(material_record)
        self.logger.info(f"{self.__class__.__name__}: 'set_target_vocabulary' method invoked - Target vocabulary set to: {self.activity.target_vocabulary}")
        return self
    
    def set_target_material(self, material_record):
        material = {
            "week": material_record[3],
            "book_title": material_record[11],
            "title": material_record[11],
            "material_type": material_record[4],
            "url": material_record[13][0]["link"]["url"]
        }
        self.activity.metadata["target_material"].append(material)
        self.logger.info(f"{self.__class__.__name__}: 'set_target_material' method invoked - Target material set to: {material}")
        return self

    # TODO - Implement this method
    def set_target_grammar(self):
        self.logger.info(f"{self.__class__.__name__}: 'set_target_grammar' method invoked - Target grammar set to: {self.activity.target_grammar}")
        return self

    def set_sentence(self):
        target_vocabulary = self.activity.target_vocabulary
        itokens = self.activity.itokens
        data_point = None
        if self.activity_blueprint_config["ms_interest_token"]["active"]:
            if self.activity_blueprint_config["ms_interest_token"]["target_student"] == "random":
                students = self.activity.metadata["sandbox_slot"]["students"]
                random_alias = students[random.randint(0, len(students) - 1)]["alias"]
                data_point = get_random_itoken(random_alias, itokens)
            else:
                data_point = get_random_itoken(self.activity_blueprint_config["ms_interest_token"]["target_student"], itokens)
        ms_interest_token_logs = {
            "data_point": data_point,
            "target_student": self.activity_blueprint_config["ms_interest_token"]["target_student"]
        }
        self.activity.metadata["ms_interest_token_logs"] = ms_interest_token_logs
        prompt = make_activity_prompt(
            prompt=self.activity_blueprint_config["prompt"],
            target_vocabulary=target_vocabulary,
            data_point=data_point,
            personalize=self.activity_blueprint_config["ms_interest_token"],
            students=self.activity.metadata["sandbox_slot"]["students"]
        )
        fm_lottie = FmLottieConnector()
        sentence = fm_lottie.make_activity_sentence(prompt)
        self.activity.sentence = sentence["sentence"]
        self.set_questions(sentence["questions"])
        self.set_image_style(sentence["media"]["style"])
        self.logger.info(f"{self.__class__.__name__}: 'set_sentence' method invoked - Sentence set to: {self.activity.sentence}")
        return self
    
    def set_questions(self, questions):
        self.activity.questions = questions
        self.logger.info(f"{self.__class__.__name__}: 'set_questions' method invoked - Options set to: {self.activity.questions}")
        return self

    def set_media(self):
        self.activity.media = {
            "style": None,
            "image_src": None,
            "text_to_speech": {
                "src": None,
                "voice": None
            },
            "background_music": {
                "src": None,
                "loop": False
            }
        }
        self.logger.info(f"{self.__class__.__name__}: 'set_media' method invoked - Media set to: {self.activity.media}")
        return self
    
    def set_image_style(self, style_prompt):
        self.activity.media["style"] = style_prompt
        self.logger.info(f"{self.__class__.__name__}: 'set_image_style' method invoked - Image style set to: {self.activity.media['style']}")
        return self
        
    def set_submitted(self):
        self.activity.submitted = False
        self.logger.info(f"{self.__class__.__name__}: 'set_submitted' method invoked - Submitted set to: {self.activity.submitted}")
        return self
    
    def build(self):
        return self.activity