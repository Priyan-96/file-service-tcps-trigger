import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="file_service_tcps_trigger",
    version="1.0.0",

    description="This CDK project consists of a lambda function.Lambda Function will be triggered on "
                "file service event and will invoke TCPS API",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "file_service_tcps_trigger"},
    packages=setuptools.find_packages(where="file_service_tcps_trigger"),

    install_requires=[
        "aws-cdk-lib==2.149.0",
        "constructs>=10.0.0,<11.0.0"
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
