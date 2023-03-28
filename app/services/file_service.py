

class FileNotAllowedException(Exception):
    """Exception raised when file not allowed."""

    def __init__(self, name="FileNotAllowed", message="le fichier n'a pas la bonne extension"):
        self.message = message
        self.name = name
        super().__init__(f'[{self.name}] {self.message}')

class InvalidFile(Exception):
    """Exception raised when file content is not correct."""

    def __init__(self, name="InvalidFile", message="le fichier contient des informations erronés"):
        self.message = message
        self.name = name
        super().__init__(f'[{self.name}] {self.message}')

def allowed_file(filename, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = {'csv'}

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions