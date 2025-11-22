from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Calculation(Base):
    __tablename__ = "calculations"
    id = Column(Integer, primary_key=True, index=True)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    op_type = Column(String(20), nullable=False)  # 'Add','Sub','Multiply','Divide'
    result = Column(Float, nullable=True)

    # IMPORTANT: Enable FK for ownership
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    def compute(self):
        if self.op_type == 'Add':
            return self.a + self.b
        if self.op_type == 'Sub':
            return self.a - self.b
        if self.op_type == 'Multiply':
            return self.a * self.b
        if self.op_type == 'Divide':
            if self.b == 0:
                raise ZeroDivisionError("Division by zero")
            return self.a / self.b
        raise ValueError("Unknown operation")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    token = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship: user → list of calculations
    calculations = relationship("Calculation", backref="user")
