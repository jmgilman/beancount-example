import requests  # type: ignore


def test_smoke(app):
    port = app.ports["8001/tcp"][0]
    url = f"http://localhost:{port}/"

    result = requests.get(url)
    content = result.text
    assert result.status_code == 200
    assert len(content) > 0

    result = requests.get(url)
    new_content = result.text
    assert result.status_code == 200
    assert content == new_content

    result = requests.get(f"{url}?reset")
    content = result.text
    assert result.status_code == 200
    assert content != new_content
