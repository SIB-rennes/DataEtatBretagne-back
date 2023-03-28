import dataclasses


@dataclasses.dataclass
class ErrorController():
    message: str

    def to_json(self):
        return {'message': self.message, 'type':'error'}

