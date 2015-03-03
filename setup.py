from setuptools import setup, find_packages

setup(
    author="Grahame Bowland",
    author_email="grahame@angrygoats.net",
    license="GPL3",
    version="0.1.0",
    packages=find_packages(),
    install_requires=['Astral', 'matplotlib', ''],
    entry_points={
        'console_scripts': [
            'snapper = snapper.cli:main',
            'pondplot = snapper.temp:main'
        ]}
    )
