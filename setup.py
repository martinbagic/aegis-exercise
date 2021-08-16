import setuptools

setuptools.setup(
    name="aging-of-evolving-genomes",
    version="2.0",
    description="",
    author="Martin Bagic, Will Bradshaw, Arian Sajina and Dario Valenzano",
    author_email="martin.bagic@outlook.com, wbradshaw@age.mpg.de, asajina@age.mpg.de, Dario.Valenzano@age.mpg.de",
    url="https://github.com/valenzano-lab/aegis",
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
    extras_require={"dev": ["pytest==6.2.4"]},
)
