from setuptools import setup, find_packages

setup(
    name="toolbox",
    version="0.1.33",
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
    url="https://github.com/Valcrist/toolbox",
    author="Valcrist",
    author_email="github@valcrist.com",
    description="Valcrist's toolbox",
)
