from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import openai
import base64
from urllib.parse import urlparse
import os
import redis.asyncio as redis

from config import config


redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)

GITHUB_TOKEN = config.GITHUB_TOKEN
openai.api_key = config.OPEN_AI_API_KEY

app = FastAPI()

class RepoAnalysisRequest(BaseModel):
    repo_url: str
    developer_level: str  # Junior, Middle, Senior
    task_description: str


def parse_github_url(url: str):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")
    if len(path_parts) >= 2:
        return path_parts[0], path_parts[1]
    else:
        raise ValueError("Invalid GitHub repository URL")


async def fetch_github_repo_files(owner: str, repo: str, path: str = ""):
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error fetching repository: {response.json().get('message', 'Unknown error')}",
            )
        return response.json()


async def fetch_all_files(owner: str, repo: str):
    cache_key = f"{owner}/{repo}"  # Ключ для кэша в Redis
    cached_data = await redis_client.get(cache_key)

    if cached_data:
        return eval(cached_data)  # Возвращаем данные из Redis

    files_content = {}

    async def process_files(items, path=""):
        for item in items:
            if item["type"] == "file":
                file_name = item["name"]
                file_content = await fetch_file_content(item["url"], file_name)
                files_content[file_name] = file_content
            elif item["type"] == "dir":
                folder_content = await fetch_github_repo_files(
                    owner, repo, path=item["path"]
                )
                await process_files(folder_content, path=item["path"])

    repo_data = await fetch_github_repo_files(owner, repo)
    await process_files(repo_data)

    # Сохраняем данные в Redis с TTL (например, 1 час)
    await redis_client.set(cache_key, str(files_content), ex=3600)
    return files_content


async def fetch_file_content(file_url: str, file_name: str):
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(file_url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error fetching file: {response.json().get('message', 'Unknown error')}",
            )

        file_data = response.json()
        file_content_base64 = file_data.get("content", "")

        try:
            content = base64.b64decode(file_content_base64).decode("utf-8")
            return content
        except Exception:
            return "[Binary or non-decodable content]"


async def review_project_with_openai(
    level: str, task_description: str, all_files_content: dict
):
    try:
        all_code = "\n\n".join(
            [f"File: {name}\n{content}" for name, content in all_files_content.items()]
        )
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert code reviewer."},
                {
                    "role": "user",
                    "content": f"Developer level: {level}\nTask description: {task_description}\n\nProject code:\n{all_code}",
                },
            ],
        )

        review_text = response.choices[0].message["content"]
        evaluation = response.choices[0].message["content"].count("good") % 5 + 1
        return {"review": review_text, "score": evaluation}

    except openai.OpenAIError as e:
        return {"review": f"OpenAI API error: {str(e)}", "score": None}


@app.post("/analyze-repo/")
async def analyze_repo(request: RepoAnalysisRequest):
    try:
        owner, repo = parse_github_url(request.repo_url)
        all_files_content = await fetch_all_files(owner, repo)
        analysis_result = await review_project_with_openai(
            request.developer_level, request.task_description, all_files_content
        )
        return analysis_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
