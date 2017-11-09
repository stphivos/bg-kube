class BlueGreenError(Exception):
    pass


class RequiredOptionError(BlueGreenError):
    def __init__(self, *args):
        super(RequiredOptionError, self).__init__('Option \'{}\' is required and was not supplied'.format(*args))


class InvalidOptionValueError(BlueGreenError):
    def __init__(self, *args):
        super(InvalidOptionValueError, self).__init__('Invalid value \'{}\' supplied for option \'{}\''.format(*args))


class ActionFailedError(BlueGreenError):
    pass
