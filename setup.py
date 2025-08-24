from setuptools import setup, find_packages


setup(
    name="mini-rag",
    version="1.0.0",
    description="This is a minimal implementation of the RAG model for question answering tasks.",
    author="3llam",
    author_email="adham.3llam@gmail.com",
    url="https://github.com/Ad7amstein/mini-rag",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    # install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [],
    },
)
