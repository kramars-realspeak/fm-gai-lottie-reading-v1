"""
Author : Peter Kramar
Email : peter@ked.tech
This module contains a class that assesses the language level of a sentence using the CEFR scale.

Requirements:
    - cefrpy # pip install cefrpy / python -m pip install cefrpy

Validate package installation by running the following commands:
    - python -c "import cefrpy"
    - python -m cefrpy validate
"""

from cefrpy import CEFRAnalyzer
from backend.helpers import setup_logger

analyzer = CEFRAnalyzer()

class TextAnalyzer:
    def __init__(self, sentence):
        self.sentence = sentence
        self.logger = setup_logger()

    def get_average_word_level_float(self, word):
        return analyzer.get_average_word_level_float(word)

    def get_average_word_level_CEFR(self, word):
        return analyzer.get_average_word_level_CEFR(word)
    
    def assess_sentence_language_level_cefrpy(self):
        self.logger.info(f"{self.__class__.__name__}: Invoking 'assess_language_level' using cefrpy for sentence: '{self.sentence}'")
        words = self.sentence[:-1].split(" ") if self.sentence[-1] == "." else self.sentence.split(" ")
        for word in words:
            self.logger.info(f"{word} : {self.get_average_word_level_CEFR(word)}")

