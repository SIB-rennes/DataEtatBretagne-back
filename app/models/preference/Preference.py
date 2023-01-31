import uuid as uuid
from marshmallow import fields
from sqlalchemy import Column, String, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app import db, ma


class Preference(db.Model):
    __tablename__ = 'preference_users'
    __table_args__ = {'schema': 'settings'}
    # PK
    id = Column(Integer, primary_key=True, nullable = False)

    # uuid
    uuid = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)

    # user
    username = Column(String, nullable = False)
    name = Column(String, nullable = False)
    # Donnée technique du filtre brut
    filters = Column(JSON, nullable = False)
    # Autre Options pour les preferences (pour les group by par exemple)
    options = Column(JSON, nullable = True)
    # Relationship
    shares = relationship("Share", lazy="select",uselist=True)


class Share(db.Model):
    __tablename__ = 'share_preference'
    __table_args__ = {'schema': 'settings'}
    # PK
    id = Column(Integer, primary_key=True, nullable = False)

    # FK
    preference_id = db.Column(Integer, db.ForeignKey('settings.preference_users.id'))
    shared_username_email = db.Column(String, nullable = False)

class SharesFormSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Share
        exclude = ('id',)

    shared_username_email = fields.Email(required=True)

class PreferenceFormSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Preference
        exclude = ('uuid',)

    filters = fields.Raw(required=True)
    shares = fields.List(fields.Nested(SharesFormSchema), required=False)

class ShareSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Share
        exclude = ('id','preference_id',)

class PreferenceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Preference
        exclude = ('id','username',)

    shares = fields.List(fields.Nested(ShareSchema), required=False)
