"""
Author : Peter Kramar
Email : peter@ked.tech
This module contains the service class for the fm-gai-lottie-true-false-v1 activity.
"""


from backend.activity import Activity
from backend.activity_blueprint_builder import FMGAILottieReadingActivityBlueprintBuilder
from backend.text_analyzer import TextAnalyzer
from backend.helpers import export_activity_blueprint_data
from backend.helpers import setup_logger
from backend.helpers import rename_log_file_to_activity_id


class ActivityBlueprintService:
    def __init__(self):
        self.builder = FMGAILottieReadingActivityBlueprintBuilder(Activity())
        self.logger = setup_logger()

    def build_activity_blueprint(self):
        self.logger.info(f"{self.__class__.__name__}: Invoking 'build_activity_blueprint' method")
        activity = (
            self.builder.set_id()
                        .set_metadata()
                        .set_sandbox_slot_record()
                        .set_itokens()
                        .set_cefr_level()
                        .set_group_alias()
                        .set_target_vocabulary()
                        .set_target_grammar()
                        .set_media()
                        .set_sentence()
                        .set_submitted()
                        .build()
        )
        activity_dict = activity.to_dict()
        export_activity_blueprint_data(activity_dict)
        rename_log_file_to_activity_id(self.logger, activity.id, "activity_blueprint")
        self.logger.info(f"{self.__class__.__name__}: Status: success. Message: Activity blueprint 'id': activity.id built successfully. Exported to data/activity_blueprint.json. This object has no history of changes so be cautious when updating it.")

    def analyze_activity_blueprint(self):
        sentence = self.builder.activity.sentence
        self.logger.info(f"{self.__class__.__name__}: Invoking 'analyze_activity_blueprint' method for sentence: '{sentence}'")
        text_analyzer = TextAnalyzer(sentence)
        text_analyzer.assess_sentence_language_level_cefrpy()
