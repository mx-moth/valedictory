from .exceptions import ValidationException


class ErrorMessageMixin(object):
    default_error_messages = {}

    def __init__(self, error_messages=None, **kwargs):
        super().__init__(**kwargs)

        messages = {}
        for c in reversed(self.__class__.__mro__):
            messages.update(getattr(c, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

    def error(self, code, params=None, cls=ValidationException, **kwargs):
        """
        Construct a validation exception.
        The message will be pulled from the :attr:`default_error_messages` dictionary
        using ``code`` as the key.
        If the error message takes format parameters,
        pass in a dict as the ``params`` argument.
        """
        message = self.error_messages[code]
        if params:
            message = message.format(**params)

        return cls(message, code=code, **kwargs)
