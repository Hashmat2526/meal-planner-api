import json
import os 

import openai


class ChatCompletion:
    def __init__(self, id, choices, created, model, object, service_tier, system_fingerprint, usage):
        self.id = id
        self.choices = choices
        self.created = created
        self.model = model
        self.object = object
        self.service_tier = service_tier
        self.system_fingerprint = system_fingerprint
        self.usage = usage

class Choice:
    def __init__(self, finish_reason, index, logprobs, message):
        self.finish_reason = finish_reason
        self.index = index
        self.logprobs = logprobs
        self.message = message

class ChatCompletionMessage:
    def __init__(self, content, refusal, role, function_call, tool_calls):
        self.content = content
        self.refusal = refusal
        self.role = role
        self.function_call = function_call
        self.tool_calls = tool_calls

class CompletionUsage:
    def __init__(self, completion_tokens, prompt_tokens, total_tokens, completion_tokens_details, prompt_tokens_details):
        self.completion_tokens = completion_tokens
        self.prompt_tokens = prompt_tokens
        self.total_tokens = total_tokens
        self.completion_tokens_details = completion_tokens_details
        self.prompt_tokens_details = prompt_tokens_details

class CompletionTokensDetails:
    def __init__(self, audio_tokens, reasoning_tokens):
        self.audio_tokens = audio_tokens
        self.reasoning_tokens = reasoning_tokens

class PromptTokensDetails:
    def __init__(self, audio_tokens, cached_tokens):
        self.audio_tokens = audio_tokens
        self.cached_tokens = cached_tokens

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

    def save_meal_plan(self, family_id, meal_plan):
         """Saves the meal plan to a .json file under a folder named by the family id."""
         try:
            folder_path = os.path.join(self.base_folder, family_id)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # Determine next available file name (1.json, 2.json, etc.)
            file_index = 1
            while os.path.exists(os.path.join(folder_path, f"{file_index}.json")):
                file_index += 1

            file_path = os.path.join(folder_path, f"{file_index}.json")
            with open(file_path, 'w') as json_file:
                json.dump(meal_plan, json_file, indent=4)

            return file_path
         except Exception as e:
            raise IOError(f"Failed to save meal plan: {e}")

