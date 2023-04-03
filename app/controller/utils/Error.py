import dataclasses


@dataclasses.dataclass
class ErrorController():
    message: str

    def to_json(self):
        if self.message is None :
            self.message = "Erreur inconnu. Merci de contacter l'administrateur."
        return {'message': self.message, 'type':'error'}


