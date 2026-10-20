"""Student analytics learning application. Demo only; no authentication or personal-data safeguards."""
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, select
from sqlalchemy.orm import DeclarativeBase, Session
from prometheus_client import make_asgi_app
import joblib
import pandas as pd

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./students.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
class Base(DeclarativeBase):
    pass
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    attendance = Column(Float, nullable=False)
    marks = Column(Float, nullable=False)
    assignment_score = Column(Float, nullable=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield

app = FastAPI(title="Saveetha Student Analytics - Portfolio Demo", version="1.0", lifespan=lifespan)
app.mount("/metrics", make_asgi_app())

class StudentIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    attendance: float = Field(ge=0, le=100)
    marks: float = Field(ge=0, le=100)
    assignment_score: float = Field(ge=0, le=100)
class StudentOut(StudentIn):
    id: int
    model_config = {"from_attributes": True}
class PredictIn(BaseModel):
    attendance: float = Field(ge=0, le=100)
    marks: float = Field(ge=0, le=100)
    assignment_score: float = Field(ge=0, le=100)

@app.get("/health")
def health():
    return {"status": "ok"}
@app.post("/students", response_model=StudentOut, status_code=201)
def create_student(body: StudentIn):
    with Session(engine) as session:
        obj = Student(**body.model_dump())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
@app.get("/students", response_model=list[StudentOut])
def list_students():
    with Session(engine) as session:
        return list(session.scalars(select(Student).order_by(Student.id)).all())
@app.get("/students/{student_id}", response_model=StudentOut)
def get_student(student_id: int):
    with Session(engine) as session:
        obj = session.get(Student, student_id)
        if obj is None:
            raise HTTPException(status_code=404, detail="Student not found")
        return obj
@app.put("/students/{student_id}", response_model=StudentOut)
def update_student(student_id: int, body: StudentIn):
    with Session(engine) as session:
        obj = session.get(Student, student_id)
        if obj is None:
            raise HTTPException(status_code=404, detail="Student not found")
        for key, value in body.model_dump().items():
            setattr(obj, key, value)
        session.commit()
        session.refresh(obj)
        return obj
@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int):
    with Session(engine) as session:
        obj = session.get(Student, student_id)
        if obj is None:
            raise HTTPException(status_code=404, detail="Student not found")
        session.delete(obj)
        session.commit()
@app.get("/reports/summary")
def summary():
    with Session(engine) as session:
        rows = list(session.scalars(select(Student)).all())
    if not rows:
        return {"count": 0, "average_marks": None, "average_attendance": None}
    return {"count": len(rows), "average_marks": round(sum(x.marks for x in rows)/len(rows),2), "average_attendance": round(sum(x.attendance for x in rows)/len(rows),2)}
@app.post("/predict")
def predict(body: PredictIn):
    path = Path(os.getenv("MODEL_PATH", "models/risk_model.joblib"))
    if not path.is_file():
        raise HTTPException(503, "Train the demo model first: python train_model.py")
    model = joblib.load(path)  # load only a model you generated and trust
    frame = pd.DataFrame([body.model_dump()])
    prediction = int(model.predict(frame)[0])
    return {"support_required": bool(prediction), "warning": "Educational synthetic-data demo; not a real academic decision tool"}
