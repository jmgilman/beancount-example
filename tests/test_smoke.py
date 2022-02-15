import requests  # type: ignore


def test_smoke(app):
    port = app.ports["8001/tcp"][0]
    url = f"http://localhost:{port}/"

    result = requests.get(url)
    assert result.status_code == 200
    assert len(result.text) > 0
