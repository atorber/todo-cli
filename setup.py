from setuptools import setup, find_packages

setup(
    name="todo-cli",
    version="0.2.5",
    description="A simple CLI tool for managing ToDo lists",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Lu Chao",
    author_email="atorber@163.com",
    url="https://github.com/atorber/todo-cli",
    packages=find_packages(),
    install_requires=[
        "simple-term-menu",
        "click>=7.0",
        "click-completion>=0.5.2",
        "PyYAML>=6.0"
    ],
    entry_points={
        "console_scripts": [
            "todo=todo_cli.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)