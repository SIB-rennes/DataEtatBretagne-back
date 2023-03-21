from dataclasses import dataclass

@dataclass
class ContextInfo:
    """Informations sur le contexte de l'appel
    Correspond aux query params 'context', 'recipient' et 'object'
    de chaque requête.
    """
    context: str
    recipient: str
    object: str