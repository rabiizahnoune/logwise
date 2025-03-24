from setuptools import setup, find_packages

setup(
    name="logwise",
    version="0.1.0",
    author="ZAHNOUNE",
    author_email="rabiizahnoune7@gmail.com",
    description="Bibliothèque Python pour analyser les logs avec un LLM",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rabiizahnoune/logwise",  # URL de votre repo GitHub
    packages=find_packages(),  # Trouve automatiquement le package 'logwise'
    install_requires=[
        "aiohttp>=3.8.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)