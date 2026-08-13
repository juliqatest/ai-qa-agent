import os


MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

BASE_URL = os.getenv(
    "BASE_URL",
    "https://www.saucedemo.com/"
)

TEST_USERNAME = os.getenv(
    "TEST_USERNAME",
    "standard_user"
)

TEST_PASSWORD = os.getenv(
    "TEST_PASSWORD",
    "secret_sauce"
)

TEST_TIMEOUT = int(
    os.getenv("TEST_TIMEOUT", "45")
)
