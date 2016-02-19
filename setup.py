from setuptools import setup, find_packages

setup(
    name="limesurveyrc2api",
    version="1.0.1",
    description="LimeSurvey RC2 API Web Services Client",
    url="https://github.com/lindsay-stevens-kirby/",
    author="Lindsay Stevens",
    author_email="lindsay.stevens.au@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    install_requires=['requests'],
    keywords="limesurvey api webservice client",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
    ],
)
