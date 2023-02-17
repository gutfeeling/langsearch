class SettingsError(Exception):
    """
    This exception should be raised when a required langsearch setting is missing or incorrectly specified in the
    Scrapy project's settings file.
    """
    pass


class IgnoreResponse(Exception):
    """
    This exception should be raised by spider middlewares when they want to ignore a response.
    """
    pass
