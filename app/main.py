from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from .models import Base
from .schemas import CalculationCreate, CalculationRead
from .crud import create_calculation, get_calculation
from app.schemas import UserCreate, UserRead, UserLogin, TokenResponse
from app.crud import create_user, authenticate_user, create_user_token

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./test.db')

# Prepare a single connect_args dict (no duplicate keyword)
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    # for psycopg2 compatible URLs, set a small connect timeout so tests don't hang
    connect_args["connect_timeout"] = 5

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(bind=engine)

app = FastAPI(title='Calculation Service (for assignment)')

@app.on_event("startup")
def on_startup():
    # Create SQLite tables automatically for local tests/dev.
    # For Postgres in CI, tests use per-test table creation or rely on the integration fixture.
    if DATABASE_URL.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/calculations', response_model=CalculationRead)
def post_calc(payload: CalculationCreate, db = Depends(get_db)):
    try:
        calc = create_calculation(db, payload, persist_result=True)
        return calc
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/calculations/{calc_id}', response_model=CalculationRead)
def read_calc(calc_id: int, db = Depends(get_db)):
    c = get_calculation(db, calc_id)
    if not c:
        raise HTTPException(404, 'Not found')
    return c

# --- User registration ---
@app.post("/users/register", response_model=UserRead)
def register(user_payload: UserCreate, db = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user_payload.username).first():
        raise HTTPException(400, "Username already exists")
    user = create_user(db, user_payload)
    return user

# --- Login ---
@app.post("/users/login", response_model=TokenResponse)
def login(payload: UserLogin, db = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    token = create_user_token(db, user)
    return {"token": token}

# --- Calculation BREAD -- using get_current_user for protected endpoints ---

@app.get("/calculations", response_model=list[CalculationRead])
def browse_calculations(db = Depends(get_db), current_user = Depends(get_current_user)):
    # return only calculations belonging to the user if user linked, else all
    return db.query(models.Calculation).filter(models.Calculation.user_id == current_user.id).all()

@app.get("/calculations/{calc_id}", response_model=CalculationRead)
def read_calculation(calc_id: int, db = Depends(get_db), current_user = Depends(get_current_user)):
    c = get_calculation(db, calc_id)
    if not c or c.user_id != current_user.id:
        raise HTTPException(404, "Not found")
    return c

@app.post("/calculations", response_model=CalculationRead)
def create_calc(payload: CalculationCreate, db = Depends(get_db), current_user = Depends(get_current_user)):
    # adapt crud.create_calculation to accept user_id
    calc = models.Calculation(a=payload.a, b=payload.b, op_type=payload.op_type.value, user_id=current_user.id)
    op = OperationFactory.get_operation(calc.op_type)
    calc.result = op.compute(calc.a, calc.b)
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc

@app.put("/calculations/{calc_id}", response_model=CalculationRead)
def update_calc(calc_id: int, payload: CalculationCreate, db = Depends(get_db), current_user = Depends(get_current_user)):
    c = get_calculation(db, calc_id)
    if not c or c.user_id != current_user.id:
        raise HTTPException(404, "Not found")
    c.a = payload.a
    c.b = payload.b
    c.op_type = payload.op_type.value
    c.result = OperationFactory.get_operation(c.op_type).compute(c.a, c.b)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@app.delete("/calculations/{calc_id}")
def delete_calc(calc_id: int, db = Depends(get_db), current_user = Depends(get_current_user)):
    c = get_calculation(db, calc_id)
    if not c or c.user_id != current_user.id:
        raise HTTPException(404, "Not found")
    db.delete(c)
    db.commit()
    return {"deleted": calc_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
