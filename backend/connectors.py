"""
Author : Peter Kramar
Email : peter@ked.tech
This module contains the logic for connecting to different external services.
"""


import json
from openai import OpenAI
from .helpers import get_current_slot_record, get_slot_records_for_date, get_course_record, get_target_material, get_target_vocabulary, get_cefr_level
from .helpers import get_secret_value
from backend.helpers import setup_logger


class FmLottieConnector:
    def __init__(self):
        self.client = OpenAI(api_key=get_secret_value('openai_key')['openai_key'])
        self.logger = setup_logger()

    def make_activity_sentence(self, prompt: str) -> str:
        self.logger.info(f"{self.__class__.__name__}: Invoking 'make_activity_sentence' method for prompt: '{prompt}'")
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "text": "You are a helpful reading activity generator for language instructors. Based on the prompt output a structured reading activity in a JSON format which contains a short reading paragraph (100 seconds reading time). Base the sentence topic on the \"target_vocabulary\". Adhere to the language level in the attribute \"cefr_level\".  You are a helpful generator for language instructors creating reading activities. Base the sentence topic on the 'target_vocabulary'. Adhere to the language level in the attribute 'cefr_level' . Your json response should return keys such as 'sentence', 'questions', 'media' : { 'style' : <best style desription goes here> }: ",
                            "type": "text"
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            temperature=1,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={
                "type": "json_object"
            }
        )
        message_content = response.choices[0].message.content
        message_content = json.loads(message_content)
        self.logger.info(f"{self.__class__.__name__}: Activity sentence generated successfully. Output: {message_content}")
        return message_content

class CourseConnector:
    def __init__(self):
        pass

    def get_current_slot_record(self, assignee):
        return get_current_slot_record(assignee)
    
    def get_slot_records_for_date(self, assignee, date):
        "Accepts date in format '1.1.2024' and returns the slot records for that date."
        return get_slot_records_for_date(assignee, date)
    
    def get_course_record(self, course_id):
        return get_course_record(course_id)
    
    def get_target_material(self, course_id, assignee, weekday):
        "Returns target material for this academic week"
        course_record = get_course_record(course_id)
        return get_target_material(course_record, assignee, weekday)
    
    def get_target_vocabulary(self, course_id, assignee, weekday):
        "Returns target vocabulary for this academic week"
        course_record = get_course_record(course_id)
        return get_target_vocabulary(course_record, assignee, weekday)
    
    def get_cefr_level(self, course_id):
        course_record = get_course_record(course_id)
        return get_cefr_level(course_record)

class ITokenConnector:
    def __init__(self):
        pass

    def get_token(self, student_alias):
        path = f"assets/itoken_local_db/{student_alias}.json"
        # return a dictionary with the token
        with open(path, 'r') as f:
            return json.load(f)