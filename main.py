import os
import sys
import requests
import openai
import re

# Load environment variables
GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GITLAB_API_URL = os.getenv('CI_API_V4_URL')
PROJECT_ID = os.getenv('CI_PROJECT_ID')
MERGE_REQUEST_IID = os.getenv('CI_MERGE_REQUEST_IID')

if not all([GITLAB_TOKEN, OPENAI_API_KEY, GITLAB_API_URL, PROJECT_ID, MERGE_REQUEST_IID]):
    print("Missing environment variables.")
    sys.exit(1)

openai.api_key = OPENAI_API_KEY

# Headers for GitLab API requests
headers = {
    'PRIVATE-TOKEN': GITLAB_TOKEN
}

def get_merge_request_description():
    url = f"{GITLAB_API_URL}/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_IID}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    mr_info = response.json()
    return mr_info.get('description', '')

def get_merge_request_comments():
    url = f"{GITLAB_API_URL}/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_IID}/notes"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    notes = response.json()
    # Exclude system notes and only include user comments
    user_comments = [note['body'] for note in notes if not note['system']]
    return '\n'.join(user_comments)

def summarize_text(text, max_tokens=150):
    if not text.strip():
        return ''
    prompt = f"Summarize the following text briefly:\n\n{text}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0.5,
        top_p=1,
        n=1,
        stop=None
    )
    summary = response.choices[0].text.strip()
    return summary

def get_merge_request_diffs():
    url = f"{GITLAB_API_URL}/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_IID}/changes"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['changes']

def analyze_code_with_ai(code_snippet, language, is_test_code, mr_summary, comments_summary):
    code_type = 'test code' if is_test_code else 'application code'
    prompt = f"""You are an experienced {language} developer.

Here is a brief summary of the merge request:
\"\"\"
{mr_summary}
\"\"\"

Here is a brief summary of the existing comments on the merge request:
\"\"\"
{comments_summary}
\"\"\"

Now, review the following {code_type}. Identify any issues with coding standards, potential bugs, and whether the code is adequately covered by tests (if applicable). Provide actionable suggestions.

Code:
\"\"\"
{code_snippet}
\"\"\"

Review:"""
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=250,
        temperature=0,
        stop=None
    )
    return response.choices[0].text.strip()

def post_inline_comment(body, file_path, new_line):
    url = f"{GITLAB_API_URL}/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_IID}/discussions"
    data = {
        'body': body,
        'position': {
            'position_type': 'text',
            'new_path': file_path,
            'new_line': new_line
        }
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

def get_language(file_path):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    language_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.jsx': 'JavaScript (React)',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript (React)',
        '.dart': 'Dart',
        # Add more mappings as needed
    }
    return language_map.get(ext, 'Programming')

def is_test_file(file_path):
    test_patterns = [
        r'test_', r'_test', r'/tests/', r'\btest\b', r'\bspec\b'
    ]
    for pattern in test_patterns:
        if re.search(pattern, file_path, re.IGNORECASE):
            return True
    return False

def parse_diff(diff_text):
    """
    Parses the diff text and yields tuples of (line_number, code)
    """
    added_line_pattern = re.compile(r'^\+(?!\+)(.*)')
    line_number = None
    for line in diff_text.split('\n'):
        if line.startswith('@@'):
            # Extract the new line number from the hunk header
            match = re.search(r'\+(\d+)', line)
            if match:
                line_number = int(match.group(1)) - 1  # Adjust for increment before yield
        elif line.startswith('+') and not line.startswith('+++'):
            line_number += 1
            code_line = line[1:]  # Remove the '+' sign
            yield (line_number, code_line)

def main():
    # Fetch and summarize MR description and comments
    mr_description = get_merge_request_description()
    mr_comments = get_merge_request_comments()
    mr_summary = summarize_text(mr_description, max_tokens=100)
    comments_summary = summarize_text(mr_comments, max_tokens=100)

    diffs = get_merge_request_diffs()

    for change in diffs:
        file_path = change['new_path']
        diff = change['diff']
        language = get_language(file_path)
        is_test = is_test_file(file_path)
        code_snippets = list(parse_diff(diff))
        for line_number, code_line in code_snippets:
            # Analyze the line with AI
            review = analyze_code_with_ai(code_line, language, is_test, mr_summary, comments_summary)
            if review:
                comment_body = f"**Issue on `{file_path}:{line_number}`**\n{review}"
                post_inline_comment(comment_body, file_path, line_number)
    print("Code review completed.")

if __name__ == "__main__":
    main()
