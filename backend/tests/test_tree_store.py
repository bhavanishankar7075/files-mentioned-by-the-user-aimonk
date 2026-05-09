from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.schemas import TagTree
from app.tree_store import create_tree, serialize_record, update_tree


def make_db() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return Session(engine)


def test_create_and_serialize_tree() -> None:
    db = make_db()
    tree = TagTree(
        name="root",
        children=[
            TagTree(name="child1", data="hello"),
            TagTree(name="child2", data="world"),
        ],
    )

    record = create_tree(db, tree)
    serialized = serialize_record(record)

    assert serialized["tree"].name == "root"
    assert serialized["tree"].children[0].data == "hello"


def test_update_replaces_existing_hierarchy() -> None:
    db = make_db()
    record = create_tree(db, TagTree(name="root", data="old"))

    updated = update_tree(
        db,
        record.id,
        TagTree(name="root", children=[TagTree(name="New Child", data="Data")]),
    )

    serialized = serialize_record(updated)
    assert serialized["tree"].children[0].name == "New Child"
