import os
from dotenv import load_dotenv

load_dotenv()
URL = os.getenv("url")

if URL.endswith("/"):
    URL = URL[:-1]

# Get the absolute path to the repository root
repo_root = os.getenv("GITHUB_WORKSPACE", os.getcwd())

# browse input data
browse_question1 = "What are typical sections in a promissory note?"
browse_question2 = "List the details of two promissory notes governed by the laws of the state of California"

# Generate input data
generate_question1 = "Generate promissory note for Washington State"
add_section = "Add Payment acceleration clause after the payment terms sections"

# Response Text Data
invalid_response = "I was unable to find content related to your query and could not generate a template. Please try again."
invalid_response1 = "An error occurred. Answers can't be saved at this time. If the problem persists, please contact the site administrator."
