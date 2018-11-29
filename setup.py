from setuptools import setup
from limesurveyrc2api import __version__

setup(
    name="limesurveyrc2api",
    version=__version__,
    description="LimeSurvey RC2 API Web Services Client",
    url="https://github.com/lindsay-stevens",
    author="Lindsay Stevens",
    author_email="lindsay.stevens.au@gmail.com",
    packages=["limesurveyrc2api"],
    test_suite="tests",
    include_package_data=True,
    license="MIT",
    install_requires=[
        # see requirements.txt
    ],
    keywords="limesurvey api webservice client",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
    ],
)
