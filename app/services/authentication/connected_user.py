
from typing import Iterable
from flask import g

from app.services.authentication.exceptions import InvalidTokenError, NoCurrentRegion
from app.utilities.exhandling import wrap_all_ex_to


class ConnectedUser():
    """
    Utilisateur connecté à l'application.
    Basiquement un wrapper à g.current_token_identity
    """
    def __init__(self, token):
        self.token = token

        self._current_roles = None
        self._current_region = None
        self._username = None
        self._sub = None
    
    @property
    def roles(self):
        """Récupère les rôle actifs sur la région actuellement connectée"""
        if self._current_roles is None:
            self._current_roles = self._retrieve_token_roles()
        return self._current_roles
    
    @property
    def current_region(self):
        """Récupère la region sur laquelle l'utilisateur est actuellement connecté"""
        if self._current_region is None:
            self._current_region = self._retrieve_token_region()
        return self._current_region
    
    @property
    def username(self):
        """Récupère l'username du token"""
        if self._username is None:
            self._username = self._retrieve_token_username()
        return self._username
    
    @property
    def sub(self):
        """Récupère le claim 'sub' du token"""
        if self._sub is None:
            self._sub = self._retrieve_token_sub()
        return self._sub
    
    @wrap_all_ex_to(InvalidTokenError)
    def _retrieve_token_roles(self):
        roles = self.token['roles'] if 'roles' in self.token else None
        assert isinstance(roles, Iterable), "Les rôles devraient être une liste"
        if roles is not None:
            roles = [x.upper() for x in roles]
        return roles
    
    @wrap_all_ex_to(NoCurrentRegion)
    def _retrieve_token_region(self):
        region = self.token['region']
        if region is None:
            raise NoCurrentRegion()
        return region
    
    @wrap_all_ex_to(InvalidTokenError)
    def _retrieve_token_username(self):
        username = self.token['username']
        if username is None:
            raise InvalidTokenError()
        return username

    @wrap_all_ex_to(InvalidTokenError)
    def _retrieve_token_sub(self):
        sub = self.token['sub']
        if sub is None:
            raise InvalidTokenError()
        return sub

    @staticmethod
    def from_current_token_identity():
        """ Crée un utilisateur connecté d'aprés un id token

        Returns:
            _type_: _description_
        
        Raises:
           InvalidTokenError
        """
        token = _current_token_identity()
        return ConnectedUser(token)

def _current_token_identity():
    token = g.current_token_identity
    if token is None:
        raise InvalidTokenError("Aucun token présent.")
    return token
