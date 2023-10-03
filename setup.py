from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='easytools',
    version='0.1',
    description="a bunch o junk",
    package_dir={"": "src"},
    packages=[#find_packages(),
              easytools.adaptive_method,
              easytools.adjumerate,
              easytools.unique_token
              ],
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    extras_require={
        "dev": ["pytest", "check-manifest", "twine"],
    },
    url="https://github.com/kilometersvi/EasyProgramming",
    author="Miles Milosevich",
    author_email="miles@milosevi.ch",
)
