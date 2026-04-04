from setuptools import setup, find_packages

setup(
    name="stitchdb",
    version="1.0.0",
    description="StitchDB database backend for Django",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="StitchDB",
    author_email="support@stitchdb.com",
    url="https://github.com/stitchdb/django",
    packages=find_packages(),
    install_requires=[
        "django>=3.2",
        "requests>=2.25.0",
    ],
    python_requires=">=3.7",
    license="MIT",
    classifiers=[
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
