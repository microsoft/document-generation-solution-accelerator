import os

from dotenv import load_dotenv

load_dotenv()
URL = os.getenv("url")

if URL.endswith("/"):
    URL = URL[:-1]

# Get the absolute path to the repository root
repo_root = os.getenv("GITHUB_WORKSPACE", os.getcwd())

# # Construct the absolute path to the JSON file
# #note: may have to remove 'Doc_gen' from below when running locally
# json_file_path = os.path.join(repo_root,'testData', 'section_title.json')

# with open(json_file_path, 'r') as file:
#     data = json.load(file)
#     sectionTitle = data['sectionTitle']

# browse input data
browse_question1 = "What are typical sections in a promissory note?"
browse_question2 = "List the details of two promissory notes governed by the laws of the state of California"

# Generate input data
generate_question1 = "Generate promissory note for Washington State"
add_section = "Add Payment acceleration clause after the payment terms sections"

# Response Text Data
invalid_response = "I was unable to find content related to your query and could not generate a template. Please try again."
