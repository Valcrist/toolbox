from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="toolbox",
    version="0.1.62",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "hexbytes",
        "colorlog",
        "pytz",
        "tzlocal",
        "aiohttp",
        "rich",
    ],
    extras_require={
        "api": [
            "uvicorn",
            "fastapi",
            "scalar-fastapi",
        ],
    },
    url="https://github.com/Valcrist/toolbox",
    author="Valcrist",
    author_email="github@valcrist.com",
    description="Valcrist's toolbox",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
