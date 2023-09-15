from setuptools import find_packages, setup

VERSION = "1.0.0"

setup(
    name="djutils",
    version=VERSION,
    author="Iago Santos",
    packages=find_packages(),
    install_requires=[
        "Django",
        "djangorestframework",
        "jsonschema",
    ],
    dependency_links=["https://github.com/iagocanalejas/pyutils.git@master#egg=pyutils"],
    include_package_data=True,
)
