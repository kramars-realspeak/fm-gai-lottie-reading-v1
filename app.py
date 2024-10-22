"""
Author : Peter Kramar
Email : peter@ked.tech
The app.py file contains the main application logic.
"""


from flask import Flask, render_template, send_from_directory
from backend.connectors import CourseConnector
from backend.activity_service import ActivityService
from backend.activity_blueprint_service import ActivityBlueprintService
from backend.helpers import setup_logger
from backend.helpers import rename_log_file_to_activity_id


app = Flask(__name__,
            template_folder='frontend/templates',
            static_folder='frontend/static')

logger = setup_logger()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/baba')
def build_activity_blueprint_automatically():
    try:
        logger.info(f"Job run started. Calling route '/baba'. Invoking 'build_activity_blueprint_automatically' method.")
        activity_blueprint_service = ActivityBlueprintService()
        activity_blueprint_service.build_activity_blueprint()
        # activity_blueprint_service.analyze_activity_blueprint()
        logger.info(f"Job run completed. Exit code 0")
        return '''
            <html>
                <head>
                    <script type="text/javascript">
                        window.onload = function() {
                            wi00 ndow.location.href = '/';
                        }
                    </script>
                </head>
                <body>
                    Activity blueprint built successfully. Validate data/activity_blueprint.json before running /build route.
                </body>
            </html>
        '''
    except Exception as e:
        return f'Error: {e}'

@app.route('/build')
def build_activity():
    try:
        logger.info(f"Job run started. Calling route '/build'. Invoking 'build_route' method.")
        activity_service = ActivityService()
        activity_service.analyze_activity()
        activity_service.build_activity()
        logger.info(f"Job run completed. Exit code 0")
        return '''
            <html>
                <head>
                    <script type="text/javascript">
                        window.onload = function() {
                            wi00 ndow.location.href = '/';
                        }
                    </script>
                </head>
                <body>
                    Activity built successfully. Redirecting...
                </body>
            </html>
        '''
    except Exception as e:
        return f'Error: {e}'

@app.route('/course/slot_record/current/<assignee>')
def current_slot(assignee):
    course = CourseConnector()
    if assignee.strip().lower() == 'cptfreedom':
        assignee = 'teacher2'
    elif assignee.strip().lower() == 'm-maker25':
        assignee = 'teacher1'
    slot = course.get_current_slot_record(assignee)
    return slot

@app.route('/course/slot_record/<date>/<assignee>')
def slot_record_by_date(date, assignee):
    course = CourseConnector()
    if assignee.strip().lower() == 'cptfreedom':
        assignee = 'teacher2'
    elif assignee.strip().lower() == 'm-maker25':
        assignee = 'teacher1'
    slot = course.get_slot_records_for_date(assignee, str(date))
    return slot

@app.route('/course/<course_id>')
def course(course_id):
    course = CourseConnector()
    course_record = course.get_course_record(course_id)
    return course_record

@app.route('/course/target_material/<course_id>/<assignee>/<weekday>')
def target_material(course_id, assignee, weekday):
    course = CourseConnector()
    if assignee.strip().lower() == 'cptfreedom':
        assignee = 'teacher2'
    elif assignee.strip().lower() == 'm-maker25':
        assignee = 'teacher1'
    material = course.get_target_material(course_id, assignee, str(weekday))
    return material

@app.route('/course/target_vocabulary/<course_id>/<assignee>/<weekday>')
def target_vocabulary(course_id, assignee, weekday):
    course = CourseConnector()
    if assignee.strip().lower() == 'cptfreedom':
        assignee = 'teacher2'
    elif assignee.strip().lower() == 'm-maker25':
        assignee = 'teacher1'
    vocabulary = course.get_target_vocabulary(course_id, assignee, str(weekday))
    return vocabulary

@app.route('/course/cefr_level/<course_id>')
def cefr_level(course_id):
    course = CourseConnector()
    level = course.get_cefr_level(course_id)
    return level

@app.route('/data/<path:filename>')
def data(filename):
    return send_from_directory('data', filename)

@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory('assets', filename)

if __name__ == '__main__':
    app.run()
