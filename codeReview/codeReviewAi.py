import openai
import os
import re
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up the OpenAI API credentials
openai.api_key = os.getenv("OPENAI_API_KEY")
system_role = os.getenv("SYSTEM_ROLE")
assistant_role = os.getenv("ASSISTANT_ROLE")
max_tokens = os.getenv("MAX_TOKENS")
model = os.getenv("MODEL")

def analyze_file_contents(file_contents, file_name):
    """
    Uses OpenAI's ChatGPT to analyze the contents of a file. Removes any comments from the file contents and 
    splits the messages into smaller chunks of at most 2000 tokens. Calls the ChatGPT API to analyze each chunk 
    and returns the response.

    Args:
    - file_contents (str): The contents of the file to analyze.
    - file_name (str): The name of the file to analyze.

    Returns:
    - The response from the ChatGPT API, or None if an error occurs.
    """
    
    print(f"Removing comments from the file contents: {file_name}")

    # # Strip any comments from the file contents
    # file_contents = re.sub(r'^\s*"""[\s\S]*?"""\s*$', '', file_contents, flags=re.MULTILINE)
    # file_contents = re.sub(r'^\s*#[\s\S]*?\s*$', '', file_contents, flags=re.MULTILINE)
    # file_contents = re.sub(r'^\s*//[\s\S]*?\s*$', '', file_contents, flags=re.MULTILINE)

    print("Splitting messages into smaller chunks of at most 2000 tokens")

    # Split the message into smaller chunks of at most 4096 tokens
    message_chunks = [file_contents[i:i + int(max_tokens)]
                      for i in range(0, len(file_contents), int(max_tokens))]
    
    response = None
    try:
        i = 1
        for chunk in message_chunks:
            print(f"Analyzing {file_name} chunk #{i}")
            i += 1

            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "assistant", "content": assistant_role},
                    {"role": "user", "content": chunk}
                ],
                max_tokens=int(max_tokens),
                n=1,
                stop=None,
                temperature=1,
            )
    except openai.error.InvalidRequestError as e:
        print(e)
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
        print("KeyboardInterrupt caught. Exiting...")
        sys.exit()
        return None

    return response
