from setuptools import setup, find_packages

setup(
    name="infinity-flow",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "click>=8.1.0",
    ],
    entry_points={
        "console_scripts": [
            "infinity-flow=infinity_flow.cli:main",
        ],
    },
    python_requires=">=3.9",
)
