from dataclasses import dataclass

@dataclass
class CallErrorDescription:
    code: str
    description: str | None

class ApiDataSubventionException(Exception):
    pass

class CallError(ApiDataSubventionException):
    """Erreur survenue lors de l'appel à l'API"""

    def __init__(self, call_error_description: CallErrorDescription) -> None:
        self.call_error_description = call_error_description