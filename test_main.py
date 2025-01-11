import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from main import app, parse_github_url, fetch_file_content, review_project_with_openai

client = TestClient(app)


# Тесты для parse_github_url
def test_parse_github_url_valid():
    owner, repo = parse_github_url("https://github.com/user/repo")
    assert owner == "user"
    assert repo == "repo"


def test_parse_github_url_invalid():
    with pytest.raises(ValueError):
        parse_github_url("https://github.com/user")


# Тест для маршрута analyze-repo
@pytest.mark.asyncio
async def test_analyze_repo_success(mocker):
    mocker.patch(
        "main.fetch_all_files", AsyncMock(return_value={"file1.py": "print('Hello')"})
    )
    mocker.patch(
        "main.review_project_with_openai",
        AsyncMock(return_value={"review": "Code is good", "score": 5}),
    )

    request_data = {
        "repo_url": "https://github.com/user/repo",
        "developer_level": "Junior",
        "task_description": "Analyze the code",
    }
    response = client.post("/analyze-repo/", json=request_data)

    assert response.status_code == 200
    assert response.json() == {"review": "Code is good", "score": 5}


# Тесты для fetch_file_content
@pytest.mark.asyncio
async def test_fetch_file_content_text(mocker):
    mock_response = AsyncMock()
    mock_response.json.return_value = {"content": "cHJpbnQoJ0hlbGxvJyk="}
    mock_response.status_code = 200
    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    content = await fetch_file_content("https://fakeurl.com/file", "file1.py")
    assert content == "print('Hello')"


@pytest.mark.asyncio
async def test_fetch_file_content_binary(mocker):
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "content": "AAECAwQFBgc="
    }  # Некодируемый контент
    mock_response.status_code = 200
    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    content = await fetch_file_content("https://fakeurl.com/file", "file1.py")
    assert content == "[Binary or non-decodable content]"


# Тесты для review_project_with_openai
@pytest.mark.asyncio
async def test_review_project_with_openai(mocker):
    mock_openai_response = AsyncMock()
    mock_openai_response.choices = [{"message": {"content": "Code is good"}}]
    mocker.patch("openai.ChatCompletion.acreate", return_value=mock_openai_response)

    result = await review_project_with_openai(
        "Junior", "Analyze the project", {"file1.py": "print('Hello')"}
    )
    assert result["review"] == "Code is good"
    assert result["score"] == 2  # Пример логики оценки
