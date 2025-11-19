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
        "gitpython>=3.1.0",
        "joblib>=1.3.0",
    ],
    extras_require={
        "full": [
            "py-tlsh>=4.7.2",
            "ppdeep",  # Python wrapper for ssdeep
            "weasyprint>=59.0",
        ],
        "pdf": ["weasyprint>=59.0"],
        "similarity": ["py-tlsh>=4.7.2", "ppdeep"],
    },
    entry_points={
        "console_scripts": [
            "forgetrace=forgetrace.cli:main",
        ],
    },
)
