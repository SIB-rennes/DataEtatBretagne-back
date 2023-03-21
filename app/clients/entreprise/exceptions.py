from . import logger

class LimitHitError(Exception):
    """Exception qui se produit lorsque la limite d'appel de l'api entreprise est atteinte."""

    def __init__(self, delay: float, default_remaining = 60) -> None:

        actual = delay
        if actual is None:
            actual = default_remaining

        self.delay = actual
        """Temps restant jusqu'à ce que la limite se réinitialise"""

class Http429Error(LimitHitError):
    """Exception qui se produit lorsque la limite d'appel de l'api entreprise est atteinte
    avec le code retour HTTP 429
    """
    def __init__(self, retry_after: str, default_delay = 60) -> None:

        delay = int(retry_after)
        if delay < 1:
            delay = default_delay
            logger.warning(f"Retry-after: {retry_after} incohérent. On attendra {default_delay}")

        super().__init__(delay)