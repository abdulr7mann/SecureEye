import openai
import os
import re
from dotenv import load_dotenv

"""
Uses OpenAI's ChatGPT to analyze the contents of a file. Removes any comments from the file contents and splits the messages into smaller chunks of at most 2000 tokens. Calls the ChatGPT API to analyze each chunk and returns the response.

Args:
file_contents (str): The contents of the file to analyze.
file_name (str): The name of the file to analyze.

Returns:
The response from the ChatGPT API, or None if an error occurs.
"""

# Set up the OpenAI API credentials
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
system_role = os.getenv("SYSTEM_ROLE2")
assistant_role = os.getenv("ASSISTANT_ROLE2")
max_tokens = os.getenv("MAX_TOKENS")
model = os.getenv("MODEL")
# Define the function to analyze the file contents using ChatGPT


def analyze_file_contents(file_contents, file_name):
    # Strip any comments from the file contents
    print(f"Removing comments from the file contents: {file_name}")
    file_contents = re.sub(
        r'^\s*"""[\s\S]*?"""\s*$', '', file_contents, flags=re.MULTILINE)
    # Remove # comments
    file_contents = re.sub(r'^\s*#[\s\S]*?\s*$',
                           '', file_contents, flags=re.MULTILINE)
    # Remove // comments
    file_contents = re.sub(
        r'^\s*//[\s\S]*?\s*$', '', file_contents, flags=re.MULTILINE)

    # Split the message into smaller chunks of at most 4096 tokens
    print("Splitting messages into smaller chunks of at most 2000 tokens")
    message_chunks = [file_contents[i:i + int(max_tokens)]
                      for i in range(0, len(file_contents), int(max_tokens))]
    # Use ChatGPT to analyze the file contents
    i = 1
    response = None
    try:
        for chunk in message_chunks:
            print(f"Analyzing {file_name} chunk #{i}")
            i = i + 1
            response = openai.ChatCompletion.create(
                model=f"{model}",
                messages=[
                    {
                        "role": "system",
                        "content": f"{system_role}"
                    },
                    {
                        "role": "assistant",
                        "content": f"{assistant_role}"
                    },
                    {
                        "role": "user",
                        "content": f"${chunk}"
                    }
                ],
                max_tokens=int(max_tokens),
                n=1,
                stop=None,
                temperature=1,
            )
    except openai.error.InvalidRequestError as e:
        print(f"{e}")
        return None
    except openai.error.APIConnectionError as e:
        print(f"Error connecting to the OpenAI API: {e}")
        return None
    except openai.error.AuthenticationError as e:
        print(f"Authentication error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        return None
    except KeyboardInterrupt:
        # Handle the exception
        print("KeyboardInterrupt caught. Exiting...")
        response = None
    # Return the analysis from ChatGPT
    return response
