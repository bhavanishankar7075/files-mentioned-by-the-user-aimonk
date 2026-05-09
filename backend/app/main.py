from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .schemas import TreeIn, TreeOut
from .tree_store import create_tree, get_all_trees, serialize_record, update_tree


Base.metadata.create_all(bind=engine)

app = FastAPI(title="AIMonk Nested Tags API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/trees", response_model=list[TreeOut])
def list_trees(db: Session = Depends(get_db)) -> list[dict]:
    return [serialize_record(record) for record in get_all_trees(db)]


@app.post("/api/trees", response_model=TreeOut, status_code=status.HTTP_201_CREATED)
def save_tree(payload: TreeIn, db: Session = Depends(get_db)) -> dict:
    record = create_tree(db, payload.tree)
    return serialize_record(record)


@app.put("/api/trees/{tree_id}", response_model=TreeOut)
def replace_tree(tree_id: int, payload: TreeIn, db: Session = Depends(get_db)) -> dict:
    record = update_tree(db, tree_id, payload.tree)
    if record is None:
        raise HTTPException(status_code=404, detail="Tree not found")

    return serialize_record(record)

