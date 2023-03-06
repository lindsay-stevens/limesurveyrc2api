from setuptools import find_packages, setup
from limesurveyrc2api import __version__

setup(
    name="limesurveyrc2api",
    version=__version__,
    description="LimeSurvey RC2 API Web Services Client",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lindsay-stevens",
    author="Lindsay Stevens",
    author_email="lindsay.stevens.au@gmail.com",
    packages=find_packages(exclude=["tests", "tests.*"]),
    test_suite="tests",
    include_package_data=True,
    license="MIT",
    install_requires=[
        "requests==2.28.2",
    ],
    keywords="limesurvey api webservice client",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
)
