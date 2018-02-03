from setuptools import setup

setup(
    name="api_scrapping",
    package=["api_scrapping"],
    include_package_data=True,
    install_requires=[
        "pymongo",
        "requests"
    ]
)
