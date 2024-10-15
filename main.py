import datetime
import json
import os
import smtplib
import threading
import time
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import bcrypt
import schedule
from flask import Flask, jsonify, request
from flask_cors import CORS

from error_handler import handle_errors
from meal_services import MealPlanSaver, MealPlanService

app = Flask(__name__)
CORS(app)

# Initialize service instances
api_key = os.getenv('OPENAI_API_KEY')
meal_plan_service = MealPlanService(api_key=api_key)
meal_plan_saver = MealPlanSaver()
user_credentials_file = 'data/user_credentials.json'

# Email configuration (ideally, these should be in environment variables)
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587



def generate_family_id():
    return str(uuid.uuid4())

# Load user credentials
def load_user_credentials():
    try:
        with open('data/user_credentials.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}  # Return an empty dict if the file doesn't exist
    except json.JSONDecodeError:
        return {}  # Return an empty dict if the file is not valid JSON


# Save user credentials
def save_user_credentials(credentials):
    with open(user_credentials_file, 'w') as file:
        json.dump(credentials, file)

def generate_hashed_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def send_email(recipient_email, username, password):
    subject = "Your Login Credentials"
    body = f"Hello {username},\n\nYour account has been created successfully!\n\n" \
           f"Email: {recipient_email}\nPassword: {password}\n\n"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_password(hashed_password, plain_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def check_existing_emails(member_restrictions):
    """Check if any of the provided emails are already registered."""
    credentials = load_user_credentials()  # Load current credentials

    for i in range(1, 5):
        email_key = f"email_{i}"
        if member_restrictions[email_key] in credentials:
            # If any email already exists, return False and the existing email
            return False, member_restrictions[email_key]

    return True, None

def update_meal_plan():
    print("Scheduler triggered: Starting meal plan update...")

    # Dummy logic for meal plan update
    current_time = datetime.datetime.now()
    print(f"Current time: {current_time}")

    # Simulating meal plan generation process
    print("Generating new meal plan...")
    time.sleep(2)  # Simulate a delay for the meal plan generation
    print("New meal plan generated successfully!")

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Schedule the job every Sunday at 12 AM
schedule.every().sunday.at("00:00").do(update_meal_plan)

# Start the schedule in a separate thread
threading.Thread(target=run_schedule, daemon=True).start()
        
@app.route('/')
def home():
    return "Server is running. Send a POST request to /webhook."

@app.route('/login', methods=['POST'])
@handle_errors
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    credentials = load_user_credentials()

    if email not in credentials:
        return jsonify({"error": "Invalid email or password"}), 401

    stored_hashed_password = credentials[email]['password']
    first_name = credentials[email]['first_name']
    last_name = credentials[email]['last_name']
    family_id = credentials[email]['family_id']    
    timestamp = credentials[email]['timestamp']

    if check_password(stored_hashed_password, password):
        # Fetch all family members excluding the logged-in user
        family_members = [
            {
                "email": member_email,
                "first_name": member_info['first_name'],
                "last_name": member_info['last_name'],
                "timestamp": member_info['timestamp']
            }
            for member_email, member_info in credentials.items()
        ]

        return jsonify({
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "family_id": family_id,
            "timestamp": timestamp,
            "family_members": family_members  # Include family members in the response
        }), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401

@app.route('/get-meal-plan', methods=['GET'])
@handle_errors
def get_meal_plan():
    # Get the family_id from the query parameters
    family_id = request.args.get('family_id')

    # Check if family_id is provided and is valid
    if family_id is None:
        return jsonify({"error": "family_id is required."}), 400
        
    # Construct the file path based on the family_id
    file_path = os.path.join('meal_plans', family_id, '1.json')

    # Check if the file exists
    if not os.path.exists(file_path):
        return jsonify({"error": "Meal plan not found for the given family ID."}), 404

    # Load the meal plan from the JSON file
    try:
        with open(file_path, 'r') as file:
             meal_plan_content = json.load(file)
    except Exception as e:
        return jsonify({"error": f"Failed to load meal plan: {str(e)}"}), 500

    # Return the meal plan content to the frontend
    return jsonify(meal_plan_content)
    
@app.route('/webhook', methods=['POST'])
@handle_errors
def webhook():
    # data = request.get_json()
    data = (request.data.decode('utf-8'))

    print(f"Request Headers: {request.headers}")
    print(f"Request Body: {data}")    
    data = json.loads(data)


    # data = json.loads(request.data.decode('utf-8'))
    
    timestamp = data.get('timestampt')
    print(f"data: {data}")

    member_restrictions = {
        "email_1": data.get('email_1',""),
        "first_name_1": data.get('first_name_1'),
        "last_name_1": data.get('last_name_1'),
        "restrictions_1": data.get('dietary_restrictions_1', 'None'),
        "email_2": data.get('email_2'),
        "first_name_2": data.get('first_name_2'),
        "last_name_2": data.get('last_name_2'),
        "restrictions_2": data.get('dietary_restrictions_2', 'None'),
        "email_3": data.get('email_3'),
        "first_name_3": data.get('first_name_3'),
        "last_name_3": data.get('last_name_3'),
        "restrictions_3": data.get('dietary_restrictions_3', 'None'),
        "email_4": data.get('email_4'),
        "first_name_4": data.get('first_name_4'),
        "last_name_4": data.get('last_name_4'),
        "restrictions_4": data.get('dietary_restrictions_4', 'None')
    }
    print(f"Member Restrictions: {member_restrictions}")

    # Check if any email is already registered
    email_check, existing_email = check_existing_emails(member_restrictions)

    if not email_check:
        # Send notification email to the person who submitted the form
        send_email(
            existing_email,
            "Meal Plan Submission Error",
            f"Your email {existing_email} is already registered. "
            "Please resubmit the form with a different email or contact support."
        )
        return jsonify({"error": "Email already registered", "email": existing_email}), 400
        
    credentials = load_user_credentials()
    
    print(f"credentials: {credentials}")
    
    family_id = generate_family_id()
    for i in range(1, 5):
        email_key = f"email_{i}"
        if member_restrictions[email_key] not in credentials:
            password = "random_password"
            hashed_password = generate_hashed_password(password)
            credentials[member_restrictions[email_key]] = {
                "first_name": member_restrictions[f"first_name_{i}"],
                "last_name": member_restrictions[f"last_name_{i}"],
                "password": hashed_password,
                "family_id": family_id,
                "timestamp": timestamp
            }
            save_user_credentials(credentials)
            send_email(
                member_restrictions[email_key], 
                member_restrictions[f"first_name_{i}"], password)

    meal_plan_prompt = (
        f"Generate a 7-day weekly meal plan for a family of four, accommodating the following dietary restrictions:\n\n"
        f"- Member 1 (First Name: {member_restrictions['first_name_1']}): {member_restrictions['restrictions_1']}\n"
        f"- Member 2 (First Name: {member_restrictions['first_name_2']}): {member_restrictions['restrictions_2']}\n"
        f"- Member 3 (First Name: {member_restrictions['first_name_3']}): {member_restrictions['restrictions_3']}\n"
        f"- Member 4 (First Name: {member_restrictions['first_name_4']}): {member_restrictions['restrictions_4']}\n\n"
        f"Each day's plan should include breakfast, lunch, and dinner for each member. Ensure the meals are balanced, "
        f"varied, and realistic for a family, using common ingredients. Avoid any restricted items mentioned above.\n\n"
        f"**Format the response in valid JSON with the following structure**:\n\n"
        f"{{\n"
        f"  \"{member_restrictions['email_1']}\": [\n"
        f"    {{ \"day\": 1, \"breakfast\": \"Meal for member 1\", \"lunch\": \"Meal for member 1\", \"dinner\": \"Meal for member 1\" }},\n"
        f"    {{ \"day\": 2, \"breakfast\": \"Meal for member 1\", \"lunch\": \"Meal for member 1\", \"dinner\": \"Meal for member 1\" }},\n"
        f"    {{ \"day\": 3, \"breakfast\": \"Meal for member 1\", \"lunch\": \"Meal for member 1\", \"dinner\": \"Meal for member 1\" }},\n"
        f"    {{ \"day\": 4, \"breakfast\": \"Meal for member 1\", \"lunch\": \"Meal for member 1\", \"dinner\": \"Meal for member 1\" }},\n"
        f"    {{ \"day\": 5, \"breakfast\": \"Meal for member 1\", \"lunch\": \"Meal for member 1\", \"dinner\": \"Meal for member 1\" }},\n"
        f"    {{ \"day\": 6, \"breakfast\": \"Meal for member 1\", \"lunch\": \"Meal for member 1\", \"dinner\": \"Meal for member 1\" }},\n"
        f"    {{ \"day\": 7, \"breakfast\": \"Meal for member 1\", \"lunch\": \"Meal for member 1\", \"dinner\": \"Meal for member 1\" }}\n"
        f"  ],\n"
        f"  \"{member_restrictions['email_2']}\": [\n"
        f"    {{ \"day\": 1, \"breakfast\": \"Meal for member 2\", \"lunch\": \"Meal for member 2\", \"dinner\": \"Meal for member 2\" }},\n"
        f"    {{ \"day\": 2, \"breakfast\": \"Meal for member 2\", \"lunch\": \"Meal for member 2\", \"dinner\": \"Meal for member 2\" }},\n"
        f"    {{ \"day\": 3, \"breakfast\": \"Meal for member 2\", \"lunch\": \"Meal for member 2\", \"dinner\": \"Meal for member 2\" }},\n"
        f"    {{ \"day\": 4, \"breakfast\": \"Meal for member 2\", \"lunch\": \"Meal for member 2\", \"dinner\": \"Meal for member 2\" }},\n"
        f"    {{ \"day\": 5, \"breakfast\": \"Meal for member 2\", \"lunch\": \"Meal for member 2\", \"dinner\": \"Meal for member 2\" }},\n"
        f"    {{ \"day\": 6, \"breakfast\": \"Meal for member 2\", \"lunch\": \"Meal for member 2\", \"dinner\": \"Meal for member 2\" }},\n"
        f"    {{ \"day\": 7, \"breakfast\": \"Meal for member 2\", \"lunch\": \"Meal for member 2\", \"dinner\": \"Meal for member 2\" }}\n"
        f"  ],\n"
        f"  \"{member_restrictions['email_3']}\": [\n"
        f"    {{ \"day\": 1, \"breakfast\": \"Meal for member 3\", \"lunch\": \"Meal for member 3\", \"dinner\": \"Meal for member 3\" }},\n"
        f"    {{ \"day\": 2, \"breakfast\": \"Meal for member 3\", \"lunch\": \"Meal for member 3\", \"dinner\": \"Meal for member 3\" }},\n"
        f"    {{ \"day\": 3, \"breakfast\": \"Meal for member 3\", \"lunch\": \"Meal for member 3\", \"dinner\": \"Meal for member 3\" }},\n"
        f"    {{ \"day\": 4, \"breakfast\": \"Meal for member 3\", \"lunch\": \"Meal for member 3\", \"dinner\": \"Meal for member 3\" }},\n"
        f"    {{ \"day\": 5, \"breakfast\": \"Meal for member 3\", \"lunch\": \"Meal for member 3\", \"dinner\": \"Meal for member 3\" }},\n"
        f"    {{ \"day\": 6, \"breakfast\": \"Meal for member 3\", \"lunch\": \"Meal for member 3\", \"dinner\": \"Meal for member 3\" }},\n"
        f"    {{ \"day\": 7, \"breakfast\": \"Meal for member 3\", \"lunch\": \"Meal for member 3\", \"dinner\": \"Meal for member 3\" }}\n"
        f"  ],\n"
        f"  \"{member_restrictions['email_4']}\": [\n"
        f"    {{ \"day\": 1, \"breakfast\": \"Meal for member 4\", \"lunch\": \"Meal for member 4\", \"dinner\": \"Meal for member 4\" }},\n"
        f"    {{ \"day\": 2, \"breakfast\": \"Meal for member 4\", \"lunch\": \"Meal for member 4\", \"dinner\": \"Meal for member 4\" }},\n"
        f"    {{ \"day\": 3, \"breakfast\": \"Meal for member 4\", \"lunch\": \"Meal for member 4\", \"dinner\": \"Meal for member 4\" }},\n"
        f"    {{ \"day\": 4, \"breakfast\": \"Meal for member 4\", \"lunch\": \"Meal for member 4\", \"dinner\": \"Meal for member 4\" }},\n"
        f"    {{ \"day\": 5, \"breakfast\": \"Meal for member 4\", \"lunch\": \"Meal for member 4\", \"dinner\": \"Meal for member 4\" }},\n"
        f"    {{ \"day\": 6, \"breakfast\": \"Meal for member 4\", \"lunch\": \"Meal for member 4\", \"dinner\": \"Meal for member 4\" }},\n"
        f"    {{ \"day\": 7, \"breakfast\": \"Meal for member 4\", \"lunch\": \"Meal for member 4\", \"dinner\": \"Meal for member 4\" }}\n"
        f"  ]\n"
        f"}}"
    )


    # Generate combined meal plan using OpenAI
    combined_meal_plan = meal_plan_service.generate_meal_plan(meal_plan_prompt)

    # Save the combined meal plan
    file_path = meal_plan_saver.save_meal_plan(family_id, meal_plan=combined_meal_plan)

    return jsonify({"message": f"Combined meal plan saved to {file_path}"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
