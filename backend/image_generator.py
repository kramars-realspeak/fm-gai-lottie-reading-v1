"""
Author : Peter Kramar
Email : peter@ked.tech
This module contains a function that generates an image based on a given sentence and target vocabulary and grammar.
"""

import io
import requests
import os
from openai import OpenAI
from backend.helpers import upload_image_to_s3, get_secret_value
from backend.helpers import setup_logger


class ImageGenerator:
    def __init__(self, activity_data):
        self.activity_data = activity_data
        self.image_size = "1792x1024"
        self.logger = setup_logger()
         
    def craft_prompt(self):
        """Crafts a prompt for DALL-E based on the input data structure."""
        self.logger.info(f"{self.__class__.__name__}: Invoking 'craft_prompt' method for DALL-E image generation.")
        sentence = self.activity_data.get("sentence")
        target_vocabulary = self.activity_data.get("target_vocabulary", [])
        style = self.activity_data['media'].get('style')
        action_phrase = sentence
        prompt = (
            f"An image showing a scene where a {', '.join(target_vocabulary)} are involved. "
            f"The scene should depict: {action_phrase}"
            f"Style: {style}."
        )
        return prompt

    def generate_image(self, image_id):
        try:
            self.logger.info(f"{self.__class__.__name__}: Invoking 'generate_image' method for image generation.")
            key= get_secret_value('openai_key')['openai_key']
            client = OpenAI(api_key=key)
            prompt = self.craft_prompt()
            response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=self.image_size,
            quality="hd",
            n=1,
            )
            image_url = response.data[0].url
            img_data = requests.get(image_url).content
            # Use an in-memory bytes buffer to avoid saving to disk
            image_file = io.BytesIO(img_data)
            image_file.name = f"{image_id}.jpg"
            self.logger.info(f"{self.__class__.__name__}: Image generated successfully.")
            upload_image_to_s3(image_file, image_id)
            image_url = 'https://s3.eu-central-1.amazonaws.com/jskramar.materials/' + image_id
            return image_url
        except Exception as e:
            self.logger.error(f"{self.__class__.__name__}: Error generating image: {e}")
            return None