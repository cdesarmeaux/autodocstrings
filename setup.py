import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("requirements-test.txt") as f:
    requirements_test = f.read().splitlines()

setuptools.setup(
    name="autodocstrings",
    version="0.1.2",
    author="Casimir Desarmeaux",
    author_email="casimir.desarmeaux@gmail.com",
    description="A tool for updating docstrings in Python files using the OpenAI API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    tests_require=requirements + requirements_test,
    test_suite="tests",
    url="https://github.com/cdesarmeaux/autodocstrings",
    packages=setuptools.find_packages(exclude=["tests*"]),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points="""
        [console_scripts]
        autodocstrings=autodocstrings.main:main
    """,
)
