import warnings


class Oops(Exception):
    def __init__(self, message):
        # for readability, always prepend exception messages in the library with two blank lines
        message = '\n\n\tOops!\n\n\t'+message.replace('\n', '\n\t')+'\n'
        super(Oops, self).__init__(message)

class Hmm(UserWarning):
    pass
