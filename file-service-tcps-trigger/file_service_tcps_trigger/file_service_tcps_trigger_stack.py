import os
from typing import List

from aws_cdk import (Stack, aws_sqs as sqs, aws_sns as sns, aws_sns_subscriptions as subscriptions,
                     aws_lambda as _lambda, aws_ssm as ssm, aws_cloudwatch_actions as cw_actions)
from aws_cdk.aws_cloudwatch import ComparisonOperator, Alarm
from aws_cdk.aws_lambda import Code, Runtime, Tracing
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from aws_cdk.aws_sqs import DeadLetterQueue
from aws_cdk.aws_logs import RetentionDays
from aws_cdk import Duration, BundlingOptions, Fn, CfnOutput
from constructs import Construct

class FileServiceTcpsTriggerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, tc_env: str, env_context: dict,
                 resource_name_suffix: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # list to add all alarms
        alarms = []

        # Create DLQ
        dlq = sqs.Queue(self, construct_id + "-DLQ", retention_period=Duration.days(14),
                        queue_name="FileServiceTCPSTriggerDLQ" + resource_name_suffix + ".fifo", fifo=True)
        tcps_trigger_dlq = DeadLetterQueue(max_receive_count=3, queue=dlq)
        # Create SQS FIFO Queue
        tcps_trigger_queue = sqs.Queue(self, construct_id + "-Queue",
                                       queue_name="FileServiceTCPSTriggerQueue" + resource_name_suffix + ".fifo",
                                       fifo=True, content_based_deduplication=True,
                                       dead_letter_queue=tcps_trigger_dlq, visibility_timeout=Duration.minutes(5))
        # Create alarm for dead letter queue
        dlq_alarm = dlq.metric_approximate_number_of_messages_visible(statistic="sum",    period=Duration.seconds(60))\
            .create_alarm(self, construct_id + "-DlqAlarm",
                          alarm_name="FileServiceTCPSTriggerDeadLetterQueueAlarm" + resource_name_suffix,
                          evaluation_periods=1,
                          comparison_operator=ComparisonOperator.GREATER_THAN_THRESHOLD,
                          threshold=0)
        alarms.append(dlq_alarm)
        # Create SNS Topic
        file_topic_export_name = "TcFileServiceTopic" + resource_name_suffix
        file_topic_arn = Fn.import_value(file_topic_export_name)
        file_topic = sns.Topic.from_topic_arn(self, construct_id + "-FileTopic", file_topic_arn)
        # Subscribe sqs to topic with filter policy
        filter_policy = {
            "FILE_ASYNC_ACTION": sns.SubscriptionFilter.string_filter(
                allowlist=["FILE_ADD", "FILE_UPDATE", "FOLDER_UPDATE","FILE_PERMISSION_CHANGE", "FOLDER_PERMISSION_CHANGE"])
        }

        file_topic.add_subscription(subscriptions.SqsSubscription(tcps_trigger_queue, filter_policy=filter_policy))

        # Create DLQ for Folder Delete Revision Queue
        folder_delete_dlq = sqs.Queue(self, "FolderDeleteRevision-DLQ",
            retention_period=Duration.days(14),
            queue_name="FolderDeleteRevisionDLQ" + resource_name_suffix + ".fifo",
            fifo=True
        )
        folder_delete_revision_dlq = DeadLetterQueue(max_receive_count=3, queue=folder_delete_dlq)

        # Create SQS FIFO Queue for Folder Delete Revision
        folder_delete_revision_queue = sqs.Queue(self, "FolderDeleteRevision-Queue",
            queue_name="FolderDeleteRevisionQueue" + resource_name_suffix + ".fifo",
            fifo=True,
            content_based_deduplication=True,
            dead_letter_queue=folder_delete_revision_dlq,
            visibility_timeout=Duration.minutes(5)
        )

        # Filter Policy for Folder Delete Revision Queue
        folder_delete_revision_filter_policy = {
            "FOLDER_ASYNC_ACTION": sns.SubscriptionFilter.string_filter(
                allowlist=["FOLDER_DELETION"]
            )
        }
        
        # Subscribe folder delete revision queue to existing topic
        file_topic.add_subscription(subscriptions.SqsSubscription(folder_delete_revision_queue, filter_policy=folder_delete_revision_filter_policy))

        # parameter store
        ssm_tid_credentials = ssm.StringParameter. \
            from_secure_string_parameter_attributes(self, construct_id + "-ssm-tid-credentials", version=1,
                                                    parameter_name="/" + tc_env + "/common/tid")

        tcps_trigger_lambda_fn = _lambda.Function(self, construct_id + "Lambda", timeout=Duration.minutes(2),
                                                  code=Code.from_asset(
                                                      path=os.getcwd() + "/functions/FileServiceTCPSTriggerFunction/",
                                                      bundling=BundlingOptions(
                                                          image=Runtime.PYTHON_3_8.bundling_image,
                                                          command=["bash", "-c", "pip install -r requirements.txt "
                                                                                 "-t /asset-output && cp -au . "
                                                                                 "/asset-output"
                                                                   ]
                                                      )),
                                                  handler="file_service_tcps_trigger_fn.handler",
                                                  runtime=Runtime.PYTHON_3_8, memory_size=1792,
                                                  description="Reads file events from sqs fifo and invokes TCPS API",
                                                  function_name="FileServiceTCPSTriggerLambda" + resource_name_suffix,
                                                  log_retention=RetentionDays.THREE_MONTHS,
                                                  environment={
                                                      "TID_CREDENTIALS_PARAMETER": ssm_tid_credentials.parameter_name,
                                                      "TCPS_BASE_URL": env_context['tcpsUrl'],
                                                      "ECOM_BASE_URL": env_context['ecomUrl'],
                                                      "ECOM_REGION": env_context['ecomRegion'],
                                                      "TC_ENVIRONMENT": tc_env.upper()
                                                  }, tracing=Tracing.ACTIVE)
        
        folder_delete_revision_lambda_fn = _lambda.Function(self, construct_id + "-Lambda",
                                            timeout=Duration.minutes(2),
                                            code=Code.from_asset(
                                                path=os.getcwd() + "/functions/FolderDeleteRevisionFunction/",
                                                bundling=BundlingOptions(
                                                    image=Runtime.PYTHON_3_8.bundling_image,
                                                    command=["bash", "-c", "pip install -r requirements.txt -t /asset-output && cp -au . /asset-output"]
                                                )
                                            ),
                                            handler="folder_delete_revision_fn.handler",
                                            runtime=Runtime.PYTHON_3_8,
                                            memory_size=1024,
                                            description="Logs folder delete revisions",
                                            function_name="FolderDeleteRevisionLambda" + resource_name_suffix,
                                            log_retention=RetentionDays.THREE_MONTHS,
                                            environment={
                                                "TID_CREDENTIALS_PARAMETER": ssm_tid_credentials.parameter_name,
                                                "TCPS_BASE_URL": env_context['tcpsUrl'],
                                                "TC_ENVIRONMENT": tc_env.upper(),
                                                "FOLDER_DELETE_REVISION_QUEUE_URL": folder_delete_revision_queue.queue_url
                                            },
                                            tracing=Tracing.ACTIVE
                                        )

        # grant access to read tid credentials from parameter store
        ssm_tid_credentials.grant_read(tcps_trigger_lambda_fn)
        ssm_tid_credentials.grant_read(folder_delete_revision_lambda_fn)
        
        # grant lambda permission to read from folder delete revision queue
        folder_delete_revision_queue.grant_consume_messages(folder_delete_revision_lambda_fn)

        # Add lambda trigger
        tcps_trigger_lambda_fn.add_event_source(SqsEventSource(tcps_trigger_queue, batch_size=1))
        folder_delete_revision_lambda_fn.add_event_source(SqsEventSource(folder_delete_revision_queue, batch_size=1))

        # Create lambda alarms for main function
        error_alarm = tcps_trigger_lambda_fn.metric_errors(statistic="p99", period=Duration.seconds(60)) \
            .create_alarm(self, construct_id + "-LambdaErrorAlarm",
                          alarm_name="FileServiceTCPSTriggerLambdaError" + resource_name_suffix,
                          evaluation_periods=1,
                          comparison_operator=ComparisonOperator.GREATER_THAN_THRESHOLD,
                          threshold=0)
        alarms.append(error_alarm)
        throttle_alarm = tcps_trigger_lambda_fn.metric_throttles(statistic="sum", period=Duration.seconds(60)) \
            .create_alarm(self, construct_id + "-LambdaThrottleAlarm",
                          alarm_name="FileServiceTCPSTriggerLambdaThrottleAlarm" + resource_name_suffix,
                          evaluation_periods=1,
                          comparison_operator=ComparisonOperator.GREATER_THAN_THRESHOLD,
                          threshold=0
                          )
        alarms.append(throttle_alarm)

        # Create lambda alarms for folder delete revision function
        folder_delete_error_alarm = folder_delete_revision_lambda_fn.metric_errors(statistic="p99", period=Duration.seconds(60)) \
            .create_alarm(self, construct_id + "-FolderDeleteRevisionLambdaErrorAlarm",
                          alarm_name="FolderDeleteRevisionLambdaError" + resource_name_suffix,
                          evaluation_periods=1,
                          comparison_operator=ComparisonOperator.GREATER_THAN_THRESHOLD,
                          threshold=0)
        alarms.append(folder_delete_error_alarm)
        folder_delete_throttle_alarm = folder_delete_revision_lambda_fn.metric_throttles(statistic="sum", period=Duration.seconds(60)) \
            .create_alarm(self, construct_id + "-FolderDeleteRevisionLambdaThrottleAlarm",
                          alarm_name="FolderDeleteRevisionLambdaThrottleAlarm" + resource_name_suffix,
                          evaluation_periods=1,
                          comparison_operator=ComparisonOperator.GREATER_THAN_THRESHOLD,
                          threshold=0
                          )
        alarms.append(folder_delete_throttle_alarm)

        self.add_alarm_action(construct_id + "-AlarmAction", alarms, tc_env)
        
        # Add Exports so that resources created in this stack can be imported in other stacks
        CfnOutput(self, construct_id + "-LambdaArnExport", value=tcps_trigger_lambda_fn.function_arn,
                  export_name="FsTcpsTriggerFunction" + resource_name_suffix)
        CfnOutput(self, construct_id + "-FolderDeleteRevisionLambdaArnExport", value=folder_delete_revision_lambda_fn.function_arn,
                  export_name="FsFolderDeleteRevisionFunction" + resource_name_suffix)
        CfnOutput(self, construct_id + "-QueueArnExport", value=tcps_trigger_queue.queue_arn,
                  export_name="FsTcpsTriggerQueue" + resource_name_suffix)
        CfnOutput(self, construct_id + "-FolderDeleteRevisionQueueArnExport", value=folder_delete_revision_queue.queue_arn,
                  export_name="FsFolderDeleteRevisionQueue" + resource_name_suffix)
        CfnOutput(self, construct_id + "-DlqArnExport", value=dlq.queue_arn,
                  export_name="FsTcpsTriggerDLQ" + resource_name_suffix)
        CfnOutput(self, construct_id + "-FolderDeleteRevisionDlqArnExport", value=folder_delete_dlq.queue_arn,
                  export_name="FsFolderDeleteRevisionDLQ" + resource_name_suffix)

    def add_alarm_action(self, construct_id: str, alarms: List[Alarm], tc_env: str):
        if tc_env != "int":
            ssm_parameter_name = "CwAlarmNotificationArn"
            if tc_env != "prod":
                ssm_parameter_name = ssm_parameter_name + "-" + tc_env
            alarm_topic_arn = ssm.StringParameter.from_string_parameter_name(self, construct_id + "-AlarmTopicArnSsm",
                                                                             ssm_parameter_name).string_value
            alarm_topic = sns.Topic.from_topic_arn(self, construct_id + "-AlarmTopic", alarm_topic_arn)
            for alarm in alarms:
                alarm.add_alarm_action(cw_actions.SnsAction(alarm_topic))
