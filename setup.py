"""Setup script for EDOT Config Explainer."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="edot-config-explainer",
    version="0.1.0",
    description="Explain EDOT Collector YAML configuration components",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Elastic",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "web": ["streamlit>=1.28.0"],
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "explain-config=explain_config.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

