"""
Author : Peter Kramar
Email : peter@ked.tech
This module contains helper functions for importing and exporting activity data.
"""


import os
import random
import shutil
import json
import boto3
import requests
from datetime import datetime
import pytz
from botocore.exceptions import BotoCoreError, ClientError
import logging
from logging.handlers import RotatingFileHandler
import logging
from datetime import datetime, timedelta


def setup_logger():
    "Returns a singleton logger instance."
    logger = logging.getLogger('job_logger')
    if not logger.hasHandlers():
        handler = RotatingFileHandler('data/logs/job.log', maxBytes=10000, backupCount=10)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.propagate = False
    return logger


def rename_log_file_to_activity_id(logger, activity_id, job_type):
    """
    Rename the log file to include the activity ID at the end of the job run.
    """
    temp_log_file = 'data/logs/job.log'
    new_log_file = f'data/logs/{job_type}_job_{activity_id}.log'
    if os.path.exists(temp_log_file):
        shutil.move(temp_log_file, new_log_file)
        logger.info(f"Log file renamed to {new_log_file}")
    else:
        logger.error(f"Temporary log file {temp_log_file} does not exist")

def upload_log_file_to_s3(activity_id, job_type):
    logger = setup_logger()
    client = boto3.client('s3', region_name='eu-central-1')
    log_file = f'data/logs/{job_type}_job_{activity_id}.log'
    key = f'job_{activity_id}.log'
    client.upload_file(log_file, 'lottie.logs', key)
    logger.info(f"Log file uploaded to S3 bucket with key: {key}")
    logger.info(f"Visit 'https://s3.eu-north-1.amazonaws.com/lottie.logs/{key}'")
    os.system(f"code {log_file}")
    return f"Log file uploaded successfully to S3 bucket."

def upload_image_to_s3(image_file, image_id):
    logger = setup_logger()
    client = boto3.client('s3', region_name='eu-central-1')   
    client.upload_fileobj(image_file, 'jskramar.materials', image_id, ExtraArgs={'ContentType': 'image/jpg', 'ContentDisposition': 'inline'})
    logger.info(f"Image uploaded to S3 bucket with key: {image_id}")
    return f"Image uploaded successfully to S3 bucket."


def get_secret_value(secret_id : str) -> str:
    "Retrieves the secret value from AWS Secrets Manager."
    secrets_manager = boto3.client('secretsmanager', region_name='eu-central-1')
    try:
        response = secrets_manager.get_secret_value(SecretId=secret_id)
        return json.loads(response['SecretString'])
    except (BotoCoreError, ClientError) as error: # pylint: disable=broad-except, unused-variable
        pass

def initialize_activity_data():
    """
    Initializes the activity data dictionary with the specified structure.
    """
    activity_data = {
            "id": "",
            "media": {
                "text_to_speech": {
                    "src": "",
                    "voice": ""
                },
                "background_music": {
                    "src": "",
                    "loop": False
                },
                "image_src": "",
                "style": ""
            },
            "sentence": "",
            "questions": {
                "1": {"sentence": "", "answer": ""},
                "2": {"sentence": "", "answer": ""},
                "3": {"sentence": "", "answer": ""},
            },
            "group_alias": "",
            "cefr_level": "",
            "target_vocabulary": [
                "",
                "",
                ""
            ],
            "target_grammar": [
                ""
            ],
            "itokens": {
                "": {}
            },
            "submitted": False,
            "metadata": {
                "organization": "",
                "analyst": "",
                "sandbox_slot": {},
                "coursework": [],
                "model_alias": "",
                "model_version": ""
            }
        }
    return activity_data

def load_activity_blueprint_config():
    path = 'config/build_activity_blueprint/config.json'
    with open(path, 'r') as file:
        return json.load(file)

def import_activity_data():
    "Imports activity data from a JSON file."
    logger = setup_logger()
    file_path = 'data/activity_blueprint.json'
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            logger.info(f"Activity data imported from {file_path}. Data : {data}")
            if len(data) == 0:
                raise Exception(f"{file_path} is empty.")
            return data
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return e

def export_activity_blueprint_data(data):
    "Exports activity data to a JSON file."
    logger = setup_logger()
    file_path = 'data/activity_blueprint.json'
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
            logger.info(f"Activity data exported to {file_path}")
            os.system(f"code {file_path}")
    except Exception as e:
        logger.error(f"Error writing {file_path}: {e}")
        return e

def export_activity_data(data):
    "Exports activity data to a JSON file."
    logger = setup_logger()
    file_path = 'data/activity.json'
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
            logger.info(f"Activity data exported to {file_path}")
            os.system(f"code {file_path}")
    except Exception as e:
        logger.error(f"Error writing {file_path}: {e}")
        return e


def append_activity_data_to_history_dataset(data):
    "Appends activity data to a JSON dataset."
    logger = setup_logger()
    file_path = 'data/history.json'
    try:
        with open(file_path, 'r') as file:
            dataset = json.load(file)
            dataset.append(data)
        with open(file_path, 'w') as file:
            json.dump(dataset, file, indent=4)
            logger.info(f"Activity data appended to {file_path}")
    except Exception as e:
        logger.error(f"Error writing to {file_path}: {e}")
        return e

def get_current_slot_record(assignee):
    """
    Retrieves the current slot record from the database.
    """
    url = "https://realspeak.ked.tech/ms_classroom_roster_manager/v1/roster/sem19?school_id=school1"
    response = requests.get(url)
    if response.status_code == 200:
        output = []
        slots = response.json()[2]
        now = datetime.now(pytz.utc)
        # now = datetime.strptime('2024-09-19 15:10:00', "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)
        for slot_id, slot in slots.items():
            start_time = datetime.strptime(slot['start_time'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)
            end_time = datetime.strptime(slot['end_time'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)
            if start_time <= now <= end_time and slot['assignee'] == assignee:
                output.append(slot)
        if len(output) == 1:
            for i, student in enumerate(output[0]['students']):
                output[0]['students'][i] = {key: student[key] for key in ['alias', 'first_name', 'last_name', 'date_of_birth'] if key in student}
            return output[0]
        elif len(output) > 1:
            raise ValueError("Multiple slots match the current date and time.")
        else:
            return []
    else:
        response.raise_for_status()


def get_slot_records_for_date(assignee, date='1.1.2024'):
    """
    Retrieves the slot records for a particular date from the database.
    """
    url = "https://realspeak.ked.tech/ms_classroom_roster_manager/v1/roster/sem19?school_id=school1"
    response = requests.get(url)
    if response.status_code == 200:
        output = []
        slots = response.json()[2]
        input_date = datetime.strptime(date, '%d.%m.%Y').date()
        for slot_id, slot in slots.items():
            slot_date = datetime.strptime(slot['start_time'], "%Y-%m-%d %H:%M:%S").date()
            if slot_date == input_date and slot['assignee'] == assignee:
                for i, student in enumerate(slot['students']):
                    slot['students'][i] = {key: student[key] for key in ['alias', 'first_name', 'last_name', 'date_of_birth'] if key in student}
                output.append(slot)
        return output
    else:
        response.raise_for_status()

def get_slot_weekday(slot_record):
    # here is the value to get it from  since slot is in due date : "due_date": "2024-09-17"
    due_date_str = slot_record['due_date']
    print(due_date_str, "DUE DATE STR")
    due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
    return due_date.weekday()

def get_course_record(course_id):
    """
    Retrieves the course record from the database.
    """
    url = f"https://realspeak.ked.tech/ms_learning_path_manager/v1/course/{course_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def is_part_of_this_week(coursework) -> bool:
    start_date_str = coursework[2]  # string e.g. '2024-09-09'
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    now = datetime.now(pytz.utc).date()
    start_of_week = now - timedelta(days=now.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    if start_of_week <= start_date <= end_of_week:
        return True
    return False


def format_coursework_id(name):
    return ''.join(e for e in name if e.isalnum()).lower()

def course_to_cefr(exam) -> str:
    """Matches exam to cefr level.

    Args:
        exam (str): The exam name.
    
    Returns:
        str: The cefr level.

    """
    cefr = ''
    if exam == 'KB0':
        cefr = 'pre-a1'
    elif exam == 'KB1':
        cefr = 'pre-a1'
    elif exam == 'STARTERS':
        cefr = 'pre-a1'
    elif exam == 'MOVERS':
        cefr = 'a1'
    elif exam == 'EMPOWER_A1':
        cefr = 'a1'
    elif exam == 'FLYERS':
        cefr = 'a2'
    elif exam == 'KEY':
        cefr = 'a2'
    elif exam == 'EMPOWER_A2':
        cefr = 'a2'
    elif exam == 'PET':
        cefr = 'b1'
    elif exam == 'EMPOWER_B1+':
        cefr = 'b1'
    elif exam == 'FCE':
        cefr = 'b2'
    elif exam == 'CAE':
        cefr = 'c1'
    elif exam == 'CPE':
        cefr = 'c2'
    return cefr

def get_cefr_level(course_record):
    """
    Retrieves the CEFR level from the course record.
    """
    course_name = course_record[2]['learning path']['PRIMARY']['main instruction']['course']
    return course_to_cefr(course_name)

def get_target_vocabulary_json(name) -> dict:
    path = 'assets/voc_local_db'
    for file in os.listdir(path):
        coursework_full_name = format_coursework_id(file.replace('json', ''))
        name = format_coursework_id(name)
        if name == coursework_full_name:
            with open(f'{path}/{file}', 'r') as f:
                return json.load(f)

def get_target_material(course_record, assignee, weekday):
    """
    Retrieves the target material from the course record.
    """
    print("RUNNING GET TARGET MATERIAL")
    output = []
    configured_courseworks = course_record[2]['learning path']['PRIMARY']['configured courseworks']
    assigned_materials = course_record[2]['learning path']['PRIMARY']['cws metadata']['assigned materials'][assignee]
    materials_for_weekday = assigned_materials.get(str(weekday))[0]
    for coursework in configured_courseworks:
        if coursework[17] in materials_for_weekday and is_part_of_this_week(coursework):
            output.append(coursework)
    return output

def get_target_vocabulary(course_record, assignee, weekday):
    """
    Retrieves the target vocabulary from the course record.
    """
    print("RUNNING GET TARGET VOCABULARY")
    target_material = get_target_material(course_record, assignee, weekday)
    print(target_material, "TARGET MATERIAL")
    target_vocabulary = []
    for material in target_material:
        print(material, "MATERIAL")
        name = material[11]
        target_vocabulary_json = get_target_vocabulary_json(name)
        target_vocabulary.append(target_vocabulary_json)
    return target_vocabulary

def get_random_itoken(student_alias: str, itokens: list):
    """
    Retrieves a random iToken for the student.
    """
    data_point = ""

    # Fetch the iTokens for the student
    student_itokens = itokens.get(student_alias, [])

    if not student_itokens:
        return data_point

    # Randomly select one of the top-level categories
    top_level_token = random.choice(student_itokens)

    # Recursive function to traverse the structure and get a random data point
    def get_random_from_dict_or_list(data):
        if isinstance(data, dict):
            # If the data is a dictionary, randomly pick one of its keys
            key = random.choice(list(data.keys()))
            return get_random_from_dict_or_list(data[key])
        elif isinstance(data, list):
            # If the data is a list, randomly pick an item from the list
            return random.choice(data)
        else:
            # If it's neither a dict nor a list, return the value directly
            return data

    data_point = get_random_from_dict_or_list(top_level_token)

    return data_point

def make_activity_prompt(prompt: dict, target_vocabulary: list, data_point, personalize : bool,  students: list):
    """
    Generates a single string prompt that describes the activity, integrates target vocabulary, 
    personalized iTokens, and provides an explanation of the expected JSON output format.
    """
    # Step 1: Initialize the prompt string
    activity_prompt = "Please generate a short reading activity containing a brief paragraph of text (100 seconds reading time) based on the following details:\n\n: "
    
    # Step 2: Include student names if required
    if prompt.get("include_ss"):
        student_names = [f"{student['first_name']} {student['last_name']}" for student in students]
        activity_prompt += f"In this activity, the students involved are: {', '.join(student_names)}.\n"
    
    # Step 3: Add custom premise if specified
    if prompt.get("premise", {}).get("include_custom_premise"):
        custom_premise = prompt["premise"].get("text", "")
        activity_prompt += f"The central theme of the activity is: \"{custom_premise}\"\n"
    
    # Step 4: Select and include random vocabulary words
    selected_vocabulary = random.sample(target_vocabulary, min(5, len(target_vocabulary)))
    activity_prompt += f"The following vocabulary words should be included and practiced: {', '.join(selected_vocabulary)}.\n"
    
    # Step 5: Personalize using iTokens if 'personalize' is true
    if personalize and data_point:
        activity_prompt += f"The scenario should be personalized around the topic \"{data_point}\", which evokes its provided description.\n"
    
    # Step 6: Explain the expected JSON output format
    activity_prompt += (
        "\nThe expected output should be in the following JSON format:\n"
        "{\n"
        "    \"media\": {\n"
        "        \"style\": \"<Describe the best style of image that visually represents the scenario here>\"\n"
        "    },\n"
        "    \"sentence\": \"<The reading activity text goes here>\",\n"
        "    \"questions\": {\n"
        "        \"1\": \"{ \"sentence\": \"<Question 1 text goes here>\", \"answer\": \"<Question 1 answer goes here>\"  }\",\n"
        "        \"2\": \"{ \"sentence\": \"<Question 2 text goes here>\", \"answer\": \"<Question 2 answer goes here>\"  }\",\n"
        "        \"3\": \"{ \"sentence\": \"<Question 3 text goes here>\", \"answer\": \"<Question 3 answer goes here>\"  }\"\n"
        "    }\n"
        "}\n"
    )
    return activity_prompt