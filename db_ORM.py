import sqlalchemy as sa
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ProofTable(Base):
    __tablename__ = 'proof_table'

    proof_key = sa.Column(sa.BigInteger(), primary_key=True, autoincrement=True)
    created_at = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)

    img_name = sa.Column(sa.VARCHAR())
    img_creation_date = sa.Column(sa.DateTime())
    img_last_update_date = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    img_device_model = sa.Column(sa.VARCHAR())
    img_format = sa.Column(sa.VARCHAR())
    img_iso = sa.Column(sa.Integer())
    img_f_number = sa.Column(sa.Float())
    img_focal_length = sa.Column(sa.Float())
    img_flash = sa.Column(sa.Integer())
    img_shutterspeed = sa.Column(sa.Float())
    img_exposure_time = sa.Column(sa.Float())
    img_dimensions = sa.Column(sa.VARCHAR())
    img_total_pixels = sa.Column(sa.Integer())
    img_color_space = sa.Column(sa.VARCHAR())
    img_color_profile = sa.Column(sa.VARCHAR())
    img_latitude = sa.Column(sa.Float())
    img_longitude = sa.Column(sa.Float())
    img_altitude = sa.Column(sa.Float())
    img_original_url = sa.Column(sa.VARCHAR())

    check_metadate_score = sa.Column(sa.Float())
    check_duplicate_score = sa.Column(sa.Float())
    check_sharpness_score = sa.Column(sa.Float())
    check_outlier_score = sa.Column(sa.Float())
    check_weather_score = sa.Column(sa.Float())

    proof_validated = sa.Column(sa.Boolean(), default=False)
    proof_validated_date = sa.Column(sa.DateTime())
    proof_validated_user = sa.Column(sa.VARCHAR())
    proof_small = sa.Column(sa.VARCHAR())
    proof_medium = sa.Column(sa.VARCHAR())
    proof_large = sa.Column(sa.VARCHAR())
    proof_notes = sa.Column(sa.VARCHAR())

    batch_key = sa.Column(sa.BigInteger, sa.ForeignKey('batch.batch_key'))

    def __repr__(self):
        return f'proof_table(proof_key={self.proof_key}, proof_date={self.proof_date})'


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


class WeatherData(Base):
    __tablename__ = 'weather_data'

    weather_key = sa.Column(sa.Integer(), primary_key=True, autoincrement=True)
    batch_key = sa.Column(sa.BigInteger, sa.ForeignKey("batch.batch_key"))
    date = sa.Column(sa.DateTime())
    weather_desc = sa.Column(sa.VARCHAR())
    three_hourly = sa.Column(sa.Integer())

    # project heeft partner
    batch_parent = relationship("Batch", back_populates="weather_data_child")
