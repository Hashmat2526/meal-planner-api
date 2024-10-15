# Family Meal Planner App

## Overview

This project is a **Family Meal Planner App** that generates customized weekly meal plans for family members based on their dietary restrictions. The application allows each family member to log in with their credentials and view their personalized meal plan.

## Features

- **User Registration and Authentication**: Family members can register using their email and name. Each member gets unique credentials sent to their email.
- **Customized Weekly Meal Plans**: The app generates a weekly meal plan for each family member according to their dietary restrictions.
- **Persistent Data Storage**: Customized meal plans are saved so that users can view them upon logging in.
- **Password Security**: User passwords are securely hashed for protection.
- **Modular Code Structure**: The code is well-organized, with meal services exported from separate files and data stored in different directories.
- **Email Verification**: If a registered email already exists, an error is thrown, and the user is notified via email.
- **Scheduled Updates**: A scheduler updates the meal plans for each family member every Sunday at 12:00 PM. This function currently has a mock implementation as proof of concept.
- **Webhook Integration**: The application integrates with Zapier, allowing it to receive data from Google Forms via a webhook. When a new row is inserted into the linked Google Sheet, Zapier triggers our webhook, which generates user credentials, emails them, and creates customized meal plans that can be fetched later by the users.

## Context

This application utilizes Google Forms for inputting family members' emails, names, and dietary restrictions. It aims to provide customized weekly meal plans tailored to each individual’s needs.

## Running on Replit

To run this application on Replit, follow these steps:

1. **Set Up Replit Environment**:

   - Go to [Replit](https://replit.com/) and create a new Python Repl.

2. **Clone the Repository**:

   - Use the following command in the Replit shell to clone the repository:
     ```bash
     git clone <your-repo-url>
     ```

3. **Install Dependencies**:

   - Ensure the required packages are installed by running:
     ```bash
     pip install -r requirements.txt
     ```

4. **Set Up Environment Variables**:

   - Before running the application, you need to set up the following secret keys as environment variables in Replit:
     - `OPENAI_API_KEY`: Your OpenAI API key for accessing the ChatGPT API.
     - `EMAIL_ADDRESS`: The email address used for sending user credentials.
     - `EMAIL_PASSWORD`: The password for the email account specified above.

   You can set these environment variables in Replit by navigating to the "Secrets" section (the lock icon) in the sidebar and adding them there.

5. **Run the Application**:
   - Start the application by running:
     ```bash
     python main.py
     ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
