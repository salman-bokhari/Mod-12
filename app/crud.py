from sqlalchemy.orm import Session
from . import models
from .factory import OperationFactory
from .schemas import CalculationCreate, UserCreate
from passlib.context import CryptContext
import uuid

# ------------------------------------------------------------------------
# Use a stable, dependency-free hashing scheme: pbkdf2_sha256
# ------------------------------------------------------------------------
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

# ------------------------------------------------------------------------
# Calculation CRUD
# ------------------------------------------------------------------------
def create_calculation(db: Session, payload: CalculationCreate, persist_result: bool = True):
    calc = models.Calculation(
        a=payload.a,
        b=payload.b,
        op_type=payload.op_type.value
    )

    op = OperationFactory.get_operation(calc.op_type)
    calc.result = op.compute(calc.a, calc.b)

    if persist_result:
        db.add(calc)
        db.commit()
        db.refresh(calc)

    return calc


def get_calculation(db: Session, calc_id: int):
    return (
        db.query(models.Calculation)
        .filter(models.Calculation.id == calc_id)
        .first()
    )


# ------------------------------------------------------------------------
# User CRUD + Auth
# ------------------------------------------------------------------------
def get_user_by_username(db: Session, username: str):
    return (
        db.query(models.User)
        .filter(models.User.username == username)
        .first()
    )


def create_user(db: Session, user_create: UserCreate):
    hashed_password = pwd_context.hash(user_create.password)

    user = models.User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None

    if not pwd_context.verify(password, user.hashed_password):
        return None

    return user


def create_user_token(db: Session, user: models.User):
    token = str(uuid.uuid4())
    user.token = token

    db.add(user)
    db.commit()
    db.refresh(user)

    return token
