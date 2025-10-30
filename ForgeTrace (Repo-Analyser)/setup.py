from setuptools import setup, find_packages

setup(
    name="forgetrace",
    version="0.1.0",
    author="Peter Kolawole",
    author_email="peter@beaconagile.net",
    description="Comprehensive IP Audit & Provenance Analysis Tool",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "jinja2>=3.1.0",
        "tlsh>=4.5.0",
        "ssdeep>=3.4",
        "gitpython>=3.1.0",
        "weasyprint>=59.0",
    ],
    entry_points={
        "console_scripts": [
            "forgetrace=forgetrace.cli:main",
        ],
    },
)
