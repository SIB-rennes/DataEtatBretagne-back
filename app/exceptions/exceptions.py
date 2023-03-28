

class DataRegatException(Exception):
    pass


class ChorusException(Exception):
    pass

class BadRequestDataRegateNum(DataRegatException):
    def __init__(self, message=""):
        self.message = message
        super().__init__(f'Bad Request : {self.message}')


class FileNotAllowedException(DataRegatException):
    """Exception raised when file not allowed."""

    def __init__(self, name="FileNotAllowed", message="le fichier n'a pas la bonne extension"):
        self.message = message
        self.name = name
        super().__init__(f'[{self.name}] {self.message}')

class InvalidFile(DataRegatException):
    """Exception raised when file content is not correct."""

    def __init__(self, name="InvalidFile", message="le fichier contient des informations erronés"):
        self.message = message
        self.name = name
        super().__init__(f'[{self.name}] {self.message}')