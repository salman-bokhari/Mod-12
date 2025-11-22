from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from .models import Base, Calculation, User
from .schemas import CalculationCreate, CalculationRead, UserCreate, UserRead, UserLogin, TokenResponse
from .crud import (
    create_calculation,
    get_calculation,
    create_user,
    authenticate_user,
    create_user_token,
)
from .factory import OperationFactory  # If you use factory pattern

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# --- Engine setup ---
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    connect_args["connect_timeout"] = 5

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine)

app = FastAPI(title="Calculation Service (for assignment)")


# --- Startup ---
@app.on_event("startup")
def startup():
    # SQLite auto-create for local dev
    if DATABASE_URL.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)


# --- DB dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------------------------------------
#                  AUTH ENDPOINTS
# ----------------------------------------------------------

@app.post("/users/register", response_model=UserRead)
def register(user_payload: UserCreate, db=Depends(get_db)):
    if db.query(User).filter(User.username == user_payload.username).first():
        raise HTTPException(400, "Username already exists")

    return create_user(db, user_payload)


@app.post("/users/login", response_model=TokenResponse)
def login(payload: UserLogin, db=Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")

    token = create_user_token(db, user)
    return {"token": token}


# ----------------------------------------------------------
#                  CALCULATION CRUD (BREAD)
# ----------------------------------------------------------

@app.post("/calculations", response_model=CalculationRead)
def add_calculation(payload: CalculationCreate, db=Depends(get_db)):
    try:
        calc = create_calculation(db, payload, persist_result=True)
        return calc
    except Exception as e:
        raise HTTPException(400, str(e))


@app.get("/calculations", response_model=list[CalculationRead])
def browse_calculations(db=Depends(get_db)):
    return db.query(Calculation).all()


@app.get("/calculations/{calc_id}", response_model=CalculationRead)
def read_calculation(calc_id: int, db=Depends(get_db)):
    c = get_calculation(db, calc_id)
    if not c:
        raise HTTPException(404, "Not found")
    return c


@app.put("/calculations/{calc_id}", response_model=CalculationRead)
def update_calculation(calc_id: int, payload: CalculationCreate, db=Depends(get_db)):
    c = get_calculation(db, calc_id)
    if not c:
        raise HTTPException(404, "Not found")

    c.a = payload.a
    c.b = payload.b
    c.op_type = payload.op
    c.result = OperationFactory.get_operation(payload.op).compute(payload.a, payload.b)

    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@app.delete("/calculations/{calc_id}")
def delete_calculation(calc_id: int, db=Depends(get_db)):
    c = get_calculation(db, calc_id)
    if not c:
        raise HTTPException(404, "Not found")

    db.delete(c)
    db.commit()
    return {"deleted": calc_id}


# ----------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
