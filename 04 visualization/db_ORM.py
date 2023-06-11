import sqlalchemy as sa
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class OrderlineContribution2(Base):
    __tablename__ = 'orderline_contribution2'

    orderline_key = sa.Column(sa.BigInteger(), primary_key=True)

    proof_name = sa.Column(sa.VARCHAR())
    proof_date = sa.Column(sa.DateTime())
    latitude = sa.Column(sa.Float())
    longitude = sa.Column(sa.Float())
    proof_small = sa.Column(sa.VARCHAR())
    proof_medium = sa.Column(sa.VARCHAR())
    proof_large = sa.Column(sa.VARCHAR())
    batch_key = sa.Column(sa.Integer())
    proof_uploaded_datetime = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    update_at = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f'orderline_contribution2(proof_name={self.proof_name}, proof_date={self.proof_date}, lat/lon={self.latitude}/{self.longitude}, batch_key={self.batch_key})'


class AllImage(Base):
    __tablename__ = 'all_images'

    proof_key = sa.Column(sa.BigInteger(), primary_key=True, autoincrement=True)
    proof_image_name = sa.Column(sa.VARCHAR())
    proof_date = sa.Column(sa.DateTime())

    latitude = sa.Column(sa.Float())
    longitude = sa.Column(sa.Float())
    altitude = sa.Column(sa.Float())
    direction = sa.Column(sa.Float())

    proof_small = sa.Column(sa.VARCHAR())
    proof_medium = sa.Column(sa.VARCHAR())
    proof_large = sa.Column(sa.VARCHAR())

    proof_uploaded_datetime = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)

    score_tree_not_tree = sa.Column(sa.Float())
    score_duplicate_tree = sa.Column(sa.Float())
    score_hash_image = sa.Column(sa.Float())
    score_rgb_image = sa.Column(sa.Float())
    score_weather = sa.Column(sa.Float())
    score_total = sa.Column(sa.Float())

    batch_key = sa.Column(sa.BigInteger, sa.ForeignKey('batch.batch_key'))

    update_at = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    valid_image_child = relationship("ValidImage", back_populates="all_image_parent", uselist=False)
    invalid_image_child = relationship("InvalidImage", back_populates="all_image_parent", uselist=False)

    batch_parent = relationship("Batch", back_populates="all_image_child")

    def __repr__(self):
        return f'allimage(proof_key={self.proof_key}, proof_date={self.proof_date})'

class ValidImage(Base):
    __tablename__ = 'valid_images'

    valid_image_id = sa.Column(sa.BigInteger(), primary_key=True, autoincrement=True)
    all_images_id = sa.Column(sa.Integer, sa.ForeignKey("all_images.proof_key"))
    date_checked = sa.Column(sa.DateTime)

    all_image_parent = relationship("AllImage", back_populates="valid_image_child")


class InvalidImage(Base):
    __tablename__ = 'invalid_images'

    invalid_image_id = sa.Column(sa.BigInteger(), primary_key=True, autoincrement=True)
    all_images_id = sa.Column(sa.Integer, sa.ForeignKey("all_images.proof_key"))
    date_checked = sa.Column(sa.DateTime)
    type_fraude = sa.Column(sa.VARCHAR)

    all_image_parent = relationship("AllImage", back_populates="invalid_image_child")


class Batch(Base):
    __tablename__ = 'batch'

    batch_key = sa.Column(sa.BigInteger(), primary_key=True, autoincrement=True)
    batch_name = sa.Column(sa.VARCHAR)
    center_long = sa.Column(sa.DECIMAL)
    center_lat = sa.Column(sa.DECIMAL)
    first_photo_upload = sa.Column(sa.DateTime)
    last_photo_upload = sa.Column(sa.DateTime)

    all_image_child = relationship("AllImage", back_populates="batch_parent")
    weather_data_child = relationship("WeatherData", back_populates="batch_parent")


class Product(Base):
    __tablename__ = 'product'

    product_key = sa.Column(sa.Integer(), primary_key=True, autoincrement=True)

    product_name = sa.Column(sa.VARCHAR())
    description = sa.Column(sa.VARCHAR())
    price = sa.Column(sa.DECIMAL())
    product_stripe_id = sa.Column(sa.VARCHAR())
    product_webflow_id = sa.Column(sa.VARCHAR())
    product_type_key = sa.Column(sa.Integer())

    created_at = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    updated_at = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    product_id_ext = sa.Column(sa.Integer())
    is_active = sa.Column(sa.BOOLEAN())

    # foreign key naar partner
    project_partner = sa.Column(sa.Integer, sa.ForeignKey("project.project_key"))

    # project heeft product
    product_child = relationship("Project", back_populates="product_parent")


class Project(Base):
    __tablename__ = 'project'

    project_key = sa.Column(sa.Integer(), primary_key=True, autoincrement=True)

    description = sa.Column(sa.VARCHAR(255))
    description_long = sa.Column(sa.VARCHAR())
    latitude = sa.Column(sa.Float())
    longitude = sa.Column(sa.Float())
    name = sa.Column(sa.VARCHAR())
    project_image_medium = sa.Column(sa.CHAR())

    # foreign key to partner
    partner_key = sa.Column(sa.Integer, sa.ForeignKey("partner.partner_key"))

    project_type_key = sa.Column(sa.Integer())
    batch_size_default = sa.Column(sa.Integer())

    created_at = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    updated_at = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    product_id_ext = sa.Column(sa.Integer())
    is_active = sa.Column(sa.BOOLEAN())

    # project heeft partner
    partner_child = relationship("Partner", back_populates="project_parent")

    # project heeft product(en)
    product_parent = relationship("Product", back_populates="product_child")


class Partner(Base):
    __tablename__ = 'partner'

    partner_key = sa.Column(sa.Integer(), primary_key=True, autoincrement=True)
    name = sa.Column(sa.VARCHAR())
    description = sa.Column(sa.VARCHAR())
    created_at = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    updated_at = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    country = sa.Column(sa.CHAR(50))
    address = sa.Column(sa.VARCHAR())
    email = sa.Column(sa.VARCHAR())
    zipcode = sa.Column(sa.VARCHAR())

    # project heeft partner
    project_parent = relationship("Project", back_populates="partner_child")


class WeatherData(Base):
    __tablename__ = 'weather_data'

    weather_key = sa.Column(sa.Integer(), primary_key=True, autoincrement=True)
    batch_key = sa.Column(sa.BigInteger, sa.ForeignKey("batch.batch_key"))
    date = sa.Column(sa.DateTime())
    weather_desc = sa.Column(sa.VARCHAR())
    three_hourly = sa.Column(sa.Integer())

    # project heeft partner
    batch_parent = relationship("Batch", back_populates="weather_data_child")
