from sqlalchemy import Column, String, Text

from app import db


class CodeProgramme(db.Model):
    __tablename__ = 'ref_code_programme'
    id = db.Column(db.Integer, primary_key=True)
    code: str = Column(String, unique=True, nullable=False)
    # FK
    code_ministere = Column(String, db.ForeignKey('ref_ministere.code'), nullable=True)
    theme = Column(db.Integer, db.ForeignKey('ref_theme.id'), nullable=True)

    label: str = Column(String)
    description: str = Column(Text)

    def __setattr__(self, key, value):
        """
        Intercept attribute setting for the instance.

        If the attribute being set is 'code' and the value is a string
        starting with '0', this method removes the first character.

        Args:
            key (str): The name of the attribute being set.
            value: The value to set the attribute to.

        Returns:
            None.

        Raises:
            TypeError: If the attribute being set is 'code' and the value
                is not a string.

        """
        if key == "code" and isinstance(value, str) and value.startswith("0"):
            value = value[1:]  # Remove the first character
        super().__setattr__(key, value)
