"""This module logs cloudwatch embedded metrics."""
import os

from aws_embedded_metrics import metric_scope, MetricsLogger


@metric_scope
def log_embedded_metrics(api_name: str, response_code: int, latency: int, metrics: MetricsLogger) -> None:
    """
    This functions logs metrics to cloudwatch in embedded metric format based on the given arguments.
    :param api_name: API identifier.
    :param response_code: response code returned by the API.
    :param latency: time taken by the API to return the response.
    :param metrics: passed by the @metric_scope decorator.
    :return:
    """
    metrics.set_namespace(f"TcpsTriggerService-{os.getenv('TC_ENVIRONMENT')}")
    metrics.set_dimensions({"API": api_name})
    metrics.put_metric("Latency", latency, "Milliseconds")
    if response_code < 300:
        metrics.put_metric("Success", 1, "Count")
    elif response_code >= 400:
        metrics.put_metric("Errors", 1, "Count")
