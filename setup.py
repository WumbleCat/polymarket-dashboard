from setuptools import setup, find_packages

setup(
    name="polymarket-analysis",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "requests>=2.31.0",
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.9",
)