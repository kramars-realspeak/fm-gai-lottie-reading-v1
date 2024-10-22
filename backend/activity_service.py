"""
Author : Peter Kramar
Email : peter@ked.tech
This module contains the service class for the fm-gai-lottie-true-false-v1 activity.
"""


from backend.activity import Activity
from backend.activity_builder import FMGAILottieReadingActivityActivityBuilder
from backend.text_analyzer import TextAnalyzer
from backend.helpers import export_activity_data
from backend.helpers import append_activity_data_to_history_dataset
from backend.helpers import setup_logger
from backend.helpers import rename_log_file_to_activity_id
from backend.helpers import upload_log_file_to_s3


class ActivityService:
    def __init__(self):
        self.builder = FMGAILottieReadingActivityActivityBuilder(Activity())
        self.logger = setup_logger()

    def analyze_activity(self):
        sentence = self.builder.data.get("sentence")
        self.logger.info(f"{self.__class__.__name__}: Invoking 'analyze_sentence' method for sentence: '{sentence}'")
        text_analyzer = TextAnalyzer(sentence)
        text_analyzer.assess_sentence_language_level_cefrpy()

    def build_activity(self):
        self.logger.info(f"{self.__class__.__name__}: Invoking 'build_activity' method")
        activity = (
            self.builder.set_id()
                        .set_metadata()
                        .set_media()
                        .set_image_src()
                        .set_itokens()
                        .set_cefr_level()
                        .set_group_alias()
                        .set_target_vocabulary()
                        .set_target_grammar()
                        .set_sentence()
                        .set_questions()
                        .set_submitted()
                        .build()
        )
        activity_dict = activity.to_dict()
        export_activity_data(activity_dict)
        append_activity_data_to_history_dataset(activity_dict)
        rename_log_file_to_activity_id(self.logger, activity.id, "activity")
        upload_log_file_to_s3(activity.id, "activity")
        return {
        "id": activity.id,
        "status": "success",
        "message": "Activity built successfully. Exported to data/output.json."
    }
