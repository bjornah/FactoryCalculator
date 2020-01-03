import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="FactoryCalculator", # Replace with your own username
    version="0.0.1",
    author="Björn Ahlgren",
    author_email="bjorn.victor.ahlgren@gmail.com",
    description="A small package to perform approximate equilibrium calculations for Factorio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bjornah/FactoryCalculator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)