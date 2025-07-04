"""This module consists of functions that help in updating the lambda logger format to json."""
import json
import logging


def get_logger():
    """
    Get the logger instance
    :return: logger instance
    """
    return logging.getLogger()


def update_logger_format(**kwargs):
    """
    Setup the logger instance based on request_id/correlation_id
    :param **kwargs: to specify extra fields and its values to be added as part of logging
    """
    for handler in logging.root.handlers:
        handler.setFormatter(JsonFormatter(**kwargs))
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)


class JsonFormatter(logging.Formatter):
    """AWS Lambda Logging formatter.

    Formats the log message as a JSON encoded string.  If the message is a
    dict it will be used directly.  If the message can be parsed as JSON, then
    the parse d value is used in the output record.
    """

    def __init__(self, **kwargs):
        """Return a JsonFormatter instance.

        The `json_default` kwarg is used to specify a formatter for otherwise
        unserialisable values.  It must not throw.  Defaults to a function that
        coerces the value to a string.

        Other kwargs are used to specify log field format strings.
        """
        super(JsonFormatter, self).__init__()
        self.format_dict = {
            'timestamp': '%(asctime)s',
            'level': '%(levelname)s',
            'location': '%(name)s.%(module)s.%(funcName)s:%(lineno)d',
        }
        self.format_dict.update(kwargs)
        self.default_json_formatter = kwargs.pop(
            'json_default', json_formatter)

    def format(self, record):
        record_dict = record.__dict__.copy()
        record_dict['asctime'] = self.formatTime(record)

        log_dict = {
            k: v % record_dict
            for k, v in self.format_dict.items()
            if v
        }

        if isinstance(record_dict['msg'], dict):
            log_dict['message'] = record_dict['msg']
        else:
            log_dict['message'] = record.getMessage()

            # Attempt to decode the message as JSON, if so, merge it with the
            # overall message for clarity.
            try:
                log_dict['message'] = json.loads(log_dict['message'])
            except (TypeError, ValueError):
                pass

        if record.exc_info and not record.exc_text:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            # from logging.Formatter:format
            record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            log_dict['exception'] = record.exc_text

        json_record = json.dumps(log_dict, default=self.default_json_formatter)

        # pragma: no cover
        if hasattr(json_record, 'decode'):
            json_record = json_record.decode('utf-8')

        return json_record


def json_formatter(obj):
    """Formatter for un-serializable values."""
    return str(obj) 