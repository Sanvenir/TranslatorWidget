
class TranslatorException(Exception):
    pass


class WebException(TranslatorException):
    pass


class ConfigException(TranslatorException):
    def __init__(self, *args):
        super().__init__("Configuration file is not set correctly", *args)
