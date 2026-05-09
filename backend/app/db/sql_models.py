from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://medlens:medlens@localhost:5432/medlens")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    dob = Column(DateTime, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    records = relationship("Record", back_populates="patient")


class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String)
    metadata_json = Column("metadata", JSON)
    predictions = relationship("Prediction", back_populates="record")
    patient = relationship("Patient", back_populates="records")


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default='technician')
    created_at = Column(DateTime, default=datetime.utcnow)


def get_user_by_username(db, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(db, username: str, hashed_password: str, role: str = 'technician'):
    user = User(username=username, hashed_password=hashed_password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("records.id"))
    label = Column(String)
    confidence = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    extras = Column(JSON)
    record = relationship("Record", back_populates="predictions")


def init_db():
    Base.metadata.create_all(bind=engine)
