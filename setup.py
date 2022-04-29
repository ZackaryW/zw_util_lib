from setuptools import setup,find_packages

setup(
    name="zw-util-lib",
    version="3.0.1",
    author="ZW",
    description="a library for misc utilities",
    long_description=''.join(open('README.md').readlines()),
    long_description_content_type="text/markdown",
    url="https://github.com/ZackaryW/zw_util_lib",
    packages=find_packages(),
    # get from requirements.txt
    install_requires= open('requirements.txt').readlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)