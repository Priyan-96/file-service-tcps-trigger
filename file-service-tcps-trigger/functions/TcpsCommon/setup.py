import setuptools

setuptools.setup(
    name="tcps_common",
    version="0.0.1",
    description="Common helpers and classes for Tcps and Revision log lambda.",
    author="author",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        "requests==2.31.0",
        "boto3==1.34.45",
        "oauthlib==3.2.2",
        "requests-oauthlib==1.3.1",
        "aws-embedded-metrics==3.2.0",
        "backoff==2.2.1",
    ],
    python_requires=">=3.7",
) 