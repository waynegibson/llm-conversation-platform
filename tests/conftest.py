import os


def pytest_configure() -> None:
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql://llm_app:change_me_securely@localhost:5432/llm_platform",
    )
