from dataclasses import dataclass

from ..utils import _InstrumentForFlaskRestx

CODE_UNKNOWN = "UNKNOWN"
CODE_CALL_FAILED = "REMOTE_CALL_FAILED"
CODE_LIMIT_HIT = "LIMIT_HIT"

@dataclass
class Error(metaclass=_InstrumentForFlaskRestx):

    code: str
    """Code de l'erreur"""

    message: str
    """Message décrivant rapidement l'exception"""

    remote_errors: tuple = tuple()
    """Structure de l'erreur de l'API distante"""