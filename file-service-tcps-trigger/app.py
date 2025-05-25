#!/usr/bin/env python3

from aws_cdk import (App, Environment, Tags)

from file_service_tcps_trigger.file_service_tcps_trigger_stack import FileServiceTcpsTriggerStack

app = App()

# Get required values from command line args

# env must be provided for adding the tag Environment. Expected values: int|qa|stage|prod
env = app.node.try_get_context("env")
if env is None:
    raise Exception("Please provide valid env")
# region must be provided . e.g. us1, eu1, ap1
region = app.node.try_get_context("region")
if region is None:
    raise Exception("Please provide valid region")

env_context = app.node.try_get_context(env)[region]

resource_name_suffix = "-" + region.upper() if env == "prod" else "-" + env.upper() + "-" + region.upper()

# StackName -> FileServiceTCPSTrigger-US1 | FileServiceTCPSTrigger-EU1 | | FileServiceTCPSTrigger-STAGE-US1 | ...
stack_name = "FileServiceTCPSTrigger" + resource_name_suffix

# aws_region here refers to AWS region, it is taken from cdk.json based on given region in command line args
account = env_context['awsAccountId']
aws_region = env_context['awsRegion']
FileServiceTcpsTriggerStack(app, stack_name, env, env_context, resource_name_suffix,
                            env=Environment(account=account, region=aws_region))

# Add following tags to the stack

# Environment -> int|qa|stage|prod
Tags.of(app).add("Environment", env)
# StackName: TC-{ENV}-FILES-{REGION} -> TC-PROD-FILES-US1 || TC-STAGE-FILES-AP1) | ...
Tags.of(app).add("StackName", env_context["stackName"])

app.synth()
