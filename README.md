Description:
GitHub OpenAI Task Checker is a tool for automated task verification on GitHub using OpenAI's capabilities. The project is designed to analyze code, check its compliance with given requirements, and identify potential errors while providing improvement suggestions.

Key Features:

Automated code review for GitHub repositories
Task compliance analysis
AI-powered feedback and recommendations
Integration with CI/CD pipelines
Technologies:

Python
GitHub API
OpenAI API
Automated code analysis scripts
Project Goal:
To provide a convenient tool for verifying developer tasks, reducing the workload of code reviewers, and improving code quality in educational and professional environments.


Step-by-Step Instructions to Start This Project Locally

Clone the Repository
If the project is hosted on GitHub, clone it using the following command:
git clone <repository_url>
Replace <repository_url> with the URL of your GitHub repository.
Navigate to the Project Directory
Move into the project's directory:
cd <project_folder_name>

Create and activate a virtual environment to isolate project dependencies:
On Windows:
python -m venv .venv
.venv\Scripts\activate
On macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate


Install Project Dependencies
Install the required packages from the requirements.txt file:
pip install -r requirements.txt


Set Up Environment Variables
Create a .env file in the root of your project.
Add the following environment variables (adjust values as needed):

OPEN_AI_API_KEY=your_openai_api_key
GITHUB_TOKEN=your_github_personal_access_token
REDIS_HOST = credentials
REDIS_PORT = credentials
Replace your_openai_api_key and your_github_personal_access_token with the appropriate API keys.

Install Redis Locally (Optional but Recommended)
If Redis is not installed locally:
Install Redis:
On macOS: Use Homebrew: brew install redis.
On Ubuntu/Debian: sudo apt install redis-server.
On Windows: Download Redis from Redis for Windows.

Start the Redis server:
redis-server

Run the Application
Start the FastAPI app using Uvicorn:
uvicorn main:app --reload
Replace main with the name of your Python file containing the FastAPI app if different.

Access the Application
http://127.0.0.1:8000

Use tools like Postman or curl to test the endpoints.
Alternatively, you can explore the automatically generated Swagger UI at:
http://127.0.0.1:8000/docs

