import uuid as uuid
from marshmallow import fields
from sqlalchemy import Column, String, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app import db, ma


class Preference(db.Model):
    __tablename__ = 'preference_users'
    # PK
    id = Column(Integer, primary_key=True, nullable = False)

    # uuid
    uuid = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)

    # user
    username = Column(String, nullable = False)
    name = Column(String, nullable = False)
    filters = Column(JSON, nullable = False)
    # Relationship
    shares = relationship("Share", lazy="select",uselist=True)


class Share(db.Model):
    __tablename__ = 'share_preference'
    # PK
    id = Column(Integer, primary_key=True, nullable = False)

    # FK
    preference_id = db.Column(Integer, db.ForeignKey('preference_users.id'))
    shared_username_email = db.Column(String, nullable = False)


class PreferenceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Preference
        exclude = ('shares','id','username',)

class PreferenceFormSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Preference
        exclude = ('shares','uuid',)

    filters = fields.Raw(required=True)

class ShareSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Share
        include_fk = True
