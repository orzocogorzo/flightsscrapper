from setuptools import setup

setup(
    name="scrapper",
    package=["scrapper"],
    include_package_data=True,
    install_requires=[
        "pymongo",
        "requests",
        "gunicorn"
    ]
)
