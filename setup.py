from setuptools import setup, find_packages

setup(
    name="limesurveyrc2api",
    version="0.0.1",
    description="LimeSurvey RC2 API Web Services Client",
    author="Lindsay Stevens",
    author_email="lindsay.stevens.au@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/lindsay-stevens-kirby/limesurveyrc2api",
    license="MIT",
    install_requires=['requests'],
)
