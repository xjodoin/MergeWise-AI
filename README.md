# **MergeWise AI** 🧠

### Smarter, Faster Code Reviews for Seamless Merging

**MergeWise AI** is an AI-powered code review tool designed to streamline your merge request process. By automating code analysis with intelligent insights, MergeWise AI enhances code quality and efficiency across multiple programming languages and frameworks. Leveraging OpenAI’s language models, it provides language-agnostic, context-aware reviews, making it an indispensable tool for diverse development teams.

---

## **Features**

- **Automated Inline Comments**: Provides precise, line-by-line feedback, highlighting potential issues, bugs, and code quality improvements.
- **Contextual Analysis**: Incorporates merge request descriptions and comments to deliver relevant, tailored insights.
- **Test Coverage Verification**: Detects newly added code and assesses if adequate tests are included.
- **Language Flexibility**: Supports Python, JavaScript, TypeScript, Dart, and more.
- **Seamless Integration with GitLab CI**: Runs automatically on every merge request, integrating directly into your CI pipeline.

---

## **Getting Started**

These instructions will guide you through setting up and running MergeWise AI in your GitLab CI pipeline.

### **Prerequisites**

- **GitLab Personal Access Token**: Ensure it has API access to read and comment on merge requests.
- **OpenAI API Key**: Required to interact with OpenAI’s models.
- **Python 3.x**: Required to run the MergeWise AI script in your GitLab CI environment.

### **Installation**

1. Clone or download this repository to your project.

2. Install the required Python packages:

   ```bash
   pip install requests openai
   ```

3. Add the necessary environment variables in GitLab:

   - `GITLAB_TOKEN`: Your GitLab personal access token.
   - `OPENAI_API_KEY`: Your OpenAI API key.

   > **Note**: Make sure to set these as protected variables in GitLab to keep them secure.

---

## **Usage**

### **Setting Up MergeWise AI in GitLab CI**

Add the following job to your `.gitlab-ci.yml` file to integrate MergeWise AI:

```yaml
stages:
  - code_review

code_review:
  stage: code_review
  image: python:3.8
  script:
    - pip install requests openai
    - python code_review.py
  rules:
    - if: '$CI_MERGE_REQUEST_IID'
  variables:
    GITLAB_TOKEN: $GITLAB_TOKEN
    OPENAI_API_KEY: $OPENAI_API_KEY
```

This configuration will run the `code_review.py` script on every merge request in the repository, automatically providing in-line feedback on code changes.

### **Running the Script Locally**

To test the script locally:

1. Clone the repository.
2. Set up a `.env` file with the required environment variables:

   ```plaintext
   GITLAB_TOKEN=<your_gitlab_token>
   OPENAI_API_KEY=<your_openai_key>
   CI_API_V4_URL=https://gitlab.com/api/v4  # Or your GitLab instance API URL
   CI_PROJECT_ID=<project_id>
   CI_MERGE_REQUEST_IID=<merge_request_iid>
   ```

3. Run the script:

   ```bash
   python code_review.py
   ```

---

## **Configuration**

### **Environment Variables**

- **`GITLAB_TOKEN`**: Personal access token for GitLab.
- **`OPENAI_API_KEY`**: OpenAI API key.
- **`CI_API_V4_URL`**: GitLab API URL (default: `https://gitlab.com/api/v4`).
- **`CI_PROJECT_ID`**: Project ID for the GitLab project.
- **`CI_MERGE_REQUEST_IID`**: Merge Request IID.

### **Code Analysis Configuration**

You can configure the script to handle specific languages and adjust prompt settings. Update the `get_language` function in the `code_review.py` file to add support for additional languages.

---

## **Development and Customization**

To extend the functionality of MergeWise AI, consider the following:

- **Additional Languages**: Add mappings in the `get_language` function to support additional file types.
- **Custom Rules**: Define new prompts or adjust the AI’s parameters in the `analyze_code_with_ai` function to apply custom code quality checks.
- **Rate Limiting and Token Optimization**: Adjust OpenAI’s `max_tokens` parameter as needed for large projects with extensive descriptions and comments.

---

## **Examples**

### **Inline Comment Example**

MergeWise AI will analyze code line by line and post comments such as:

> **Issue on `file.py:23`**  
> The variable `x` is used but never defined. Consider defining it or removing it if unused.

### **Global Comment Example**

For overall issues or advice, MergeWise AI posts global comments like:

> **General Feedback**  
> This merge request introduces new logic in `module.js` but lacks corresponding test coverage. Adding tests would ensure reliability.

---

## **Contributing**

We welcome contributions! Feel free to open issues, suggest improvements, or submit pull requests. For major changes, please discuss them first to ensure they align with the project goals.

---

## **Security**

- Store sensitive tokens as environment variables and set them as **protected** in GitLab CI.
- Avoid exposing API keys in logs or error messages.

---

## **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## **Contact**

For questions or feedback, reach out at **[mergewise@support.com](mailto:mergewise@support.com)**.

---

Thank you for using **MergeWise AI**! We hope it makes your code review process faster, easier, and more effective.
