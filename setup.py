import setuptools

setuptools.setup(
    name="aegis",
    version="2.0.1",
    description="",
    package_dir={"": "src"},
    packages=["aegis"],
    python_requires=">=3.6",
    scripts=["scripts/aegis"],
    install_requires=[
        "numpy>=1.21.1",
        "pandas>=1.2",
        "pyyaml>=5.4.1",
        "pyarrow>=5.0.0",
    ],
    extras_require = {
        "dev": [
            "pytest==6.2.4"
        ]
    }
)
