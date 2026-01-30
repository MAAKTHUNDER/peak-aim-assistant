from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="peak-aim-assistant",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Professional Peak & Aim assistant for GameLoop emulator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_USERNAME/peak-aim-assistant",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt5>=5.15.0",
        "keyboard>=0.13.5",
        "pynput>=1.7.6",
        "pywin32>=305",
    ],
    entry_points={
        "console_scripts": [
            "peak-aim=peak_aim_assistant:main",
        ],
    },
)
