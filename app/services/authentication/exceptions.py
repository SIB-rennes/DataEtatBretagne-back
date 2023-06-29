
class AuthenticationModuleError(Exception):
    pass

class InvalidTokenError(AuthenticationModuleError):
    """Exception en case de token non présent"""
    pass

class NoCurrentRegion(InvalidTokenError):
    """Exception raised when requesting current region and its not available"""
    pass