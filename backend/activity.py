"""
Author : Peter Kramar
Email : peter@ked.tech
This module contains the builder class for fm-gai-lottie-true-false-v1 activity objects.
"""


class Activity:
    def __init__(self):
        self.id = None
        self.media = None
        self.sentence = None
        self.questions = None
        self.group_alias = None
        self.cefr_level = None
        self.target_vocabulary = None
        self.target_grammar = None
        self.itokens = None
        self.submitted = None
        self.metadata = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "media": self.media,
            "sentence": self.sentence,
            "questions": self.questions,
            "group_alias": self.group_alias,
            "cefr_level": self.cefr_level,
            "target_vocabulary": self.target_vocabulary,
            "target_grammar": self.target_grammar,
            "itokens": self.itokens,
            "submitted": self.submitted,
            "metadata": self.metadata
        }
    
    def from_dict(self, data):
        self.id = data["id"]
        self.media = data["media"]
        self.sentence = data["sentence"]
        self.questions = data["questions"]
        self.group_alias = data["group_alias"]
        self.cefr_level = data["cefr_level"]
        self.target_vocabulary = data["target_vocabulary"]
        self.target_grammar = data["target_grammar"]
        self.itokens = data["itokens"]
        self.submitted = data["submitted"]
        self.metadata = data["metadata"]
        return self
    
    def __str__(self):
        return f"Activity: {self.id} - {self.sentence}"