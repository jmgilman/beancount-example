from pytest_docker_tools import build, container  # type: ignore

app_image = build(path=".")
app = container(
    image="{app_image.id}",
    ports={
        "8001/tcp": None,
    },
)
