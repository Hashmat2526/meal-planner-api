import json
import os 

import openai

# Service layer for handling meal plan generation
class MealPlanService:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API key is missing. Please set your OpenAI API key.")
        openai.api_key = api_key

    def generate_meal_plan(self, prompt):

        # Make the OpenAI API call
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096  # You can adjust the token limit based on your needs
        )

        return response.choices[0].message.content


# Service layer for saving meal plans to JSON
class MealPlanSaver:
    def __init__(self, base_folder="meal_plans"):
        self.base_folder = base_folder

    def save_meal_plan(self, family_id, meal_plan, file_name=None):
        """Saves the meal plan to a .json file under a folder named by the family id."""
        try:
            # Create the folder path based on the family ID
            folder_path = os.path.join(self.base_folder, family_id)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # Use the provided file_name or default to "1.json"
            file_name = "1"
            file_path = os.path.join(folder_path, f"{file_name}.json")

            # Save the meal plan to the file
            with open(file_path, 'w') as json_file:
                json.dump(meal_plan, json_file, indent=4)

            return file_path
        except Exception as e:
            raise IOError(f"Failed to save meal plan: {e}")


    def save_member_restrictions(self, family_id, meal_plan, file_name=None):
        """Saves the meal plan to a member_restrictions.json file under a folder named by the family id."""
        try:
            # Create the folder path based on the family ID
            folder_path = os.path.join(self.base_folder, family_id)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # Use the provided file_name or default to "1.json"
            file_name = "member_restrictions"
            file_path = os.path.join(folder_path, f"{file_name}.json")

            # Save the meal plan to the file
            with open(file_path, 'w') as json_file:
                json.dump(meal_plan, json_file, indent=4)

            return file_path
        except Exception as e:
            raise IOError(f"Failed to save meal plan: {e}")

