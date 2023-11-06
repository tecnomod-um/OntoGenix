import os
import json
import openai

# Setting OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def create_initial_context():
    print('create_initial_context')

def generate_ontology():
    print('generate_ontology')

def create_mapping():
    print('create_mapping')

def exit():
    print("exit")

AVAILABLE_FUNCTIONS = {
    "create_initial_context": create_initial_context,
    "generate_ontology": generate_ontology,
    "create_mapping": create_mapping,
    "exit":exit
}

def select_process(method: str):
    AVAILABLE_FUNCTIONS[method]()

def create_initial_response(messages, function_data, function_name):
    """Generates an initial response from OpenAI's GPT-3 model using user's message."""
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        functions=function_data,
        function_call={"name": function_name}
    )

def process_function_response(response, function_to_call):
    """Processes the response message from model and calls the intended function."""
    response_message = response["choices"][0]["message"]
    function_name = response_message["function_call"]["name"]
    function_args = json.loads(response_message["function_call"]["arguments"])
    function_response = function_to_call(**function_args)
    return function_response




# Defining the data for 'select_method' function
functions_data = [
    {
      "name": "select_process",
      "description": "Can select the engineering step for creating an ontology using LLMs",
      "parameters": {
        "type": "object",
        "properties": {
          "method": {"type": "string", "enum": ["create_initial_context", "generate_ontology", "create_mapping", "exit"],
                  "description": "Ontology engineering self-assembling program interface."},
        }
      }
    }
]


user_message = '''propose an ontology based on the given json dataset'''

user_message = '''Generate the mapping'''

initial_message = {
    "role": "assistant",
    "content": user_message
}
# Creating initial Response
response = create_initial_response(
    [initial_message],
    functions_data,
    "select_process"
)
# Process the response and order pizza
process_function_response(response, select_process)

print('fin')