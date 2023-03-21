
def _dict_get_nested(dict, *keys, default = None):
    """Récupère les valeurs imbriquées dans un dictionnaire

    Exemple:

    d = { 'a': { 'b': { 'c': 'foo' }  } }
    nested = _get_nested(d, 'a', 'b', 'c') # nested == 'foo'
    nested = _get_nested(d, 'does', 'not', 'exist') # nested == None


    Args:
        dict (_type_): Structure à parcourir
        default (_type_, optional): Valeur par défaut en cas de clef inexistante. Defaults to None.
    """

    v = dict
    for key in keys:
        try:
            v = v.get(key, default)
        except AttributeError:
            v = default
            break
    return v
