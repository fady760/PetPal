import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from models import Base, Pet

# ---------------------------------------------------------------------------
# Database Configuration
# ---------------------------------------------------------------------------
# Reads DATABASE_URL from environment variable (e.g., mysql+pymysql://root:root@localhost:3306/petpal)
# Falls back to SQLite for instant local development and testing.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./petpal.db")

connect_args = {}
engine_kwargs = {"pool_pre_ping": True}

if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    # pool_pre_ping is not supported or needed on standard sqlite static pool
    engine_kwargs.pop("pool_pre_ping", None)

engine = create_engine(DATABASE_URL, connect_args=connect_args, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure tables exist on module initialization
Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to yield a SQLAlchemy session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_initial_data(db: Session):
    """Seed sample pets if the database is empty for demo purposes."""
    if db.query(Pet).count() == 0:
        sample_pets = [
            Pet(
                name="Milo",
                species="Dog",
                age=2,
                is_adopted=False,
                image_url="https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=600&q=80",
            ),
            Pet(
                name="Luna",
                species="Cat",
                age=1,
                is_adopted=False,
                image_url="https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=600&q=80",
            ),
            Pet(
                name="Bella",
                species="Dog",
                age=3,
                is_adopted=False,
                image_url="https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=600&q=80",
            ),
            Pet(
                name="Oliver",
                species="Cat",
                age=4,
                is_adopted=True,
                image_url="https://images.unsplash.com/photo-1533738363-b7f9aef128ce?auto=format&fit=crop&w=600&q=80",
            ),
        ]
        db.add_all(sample_pets)
        db.commit()


# ---------------------------------------------------------------------------
# Application Lifespan & Initialization
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    # Seed initial demo data
    with SessionLocal() as db:
        seed_initial_data(db)
    yield


app = FastAPI(
    title="PetPal - Pet Adoption Tracker",
    description="A modern, lightweight pet adoption tracker built for DevOps pipelines.",
    version="1.0.0",
    lifespan=lifespan,
)

# Jinja2 Templates Setup
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    """Render the main PetPal page with the pet adoption cards grid."""
    pets = db.query(Pet).order_by(Pet.is_adopted.asc(), Pet.id.desc()).all()
    available_count = db.query(Pet).filter(Pet.is_adopted == False).count()
    adopted_count = db.query(Pet).filter(Pet.is_adopted == True).count()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "pets": pets,
            "available_count": available_count,
            "adopted_count": adopted_count,
            "total_count": len(pets),
        },
    )


@app.post("/pets")
def add_pet(
    name: str = Form(...),
    species: str = Form(...),
    age: int = Form(...),
    image_url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Add a new pet to the tracker."""
    new_pet = Pet(
        name=name.strip(),
        species=species.strip(),
        age=age,
        image_url=image_url.strip() if image_url and image_url.strip() else None,
        is_adopted=False,
    )
    db.add(new_pet)
    db.commit()
    db.refresh(new_pet)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/pets/{pet_id}/adopt")
def mark_pet_adopted(pet_id: int, db: Session = Depends(get_db)):
    """Update pet's status to 'Adopted'."""
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    pet.is_adopted = True
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    """
    DevOps Health Check Endpoint.
    Performs a simple SELECT 1 against the configured database to ensure connectivity.
    Returns HTTP 200 with {'status': 'healthy', 'database': 'connected'}.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(exc),
            },
        )
