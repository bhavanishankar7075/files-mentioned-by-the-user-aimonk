from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .models import TagNode, TreeRecord
from .schemas import TagTree


def create_tree(db: Session, tree: TagTree) -> TreeRecord:
    record = TreeRecord()
    db.add(record)
    db.flush()

    # Flush gives the tree record an id before its recursive nodes are inserted.
    db.add(_to_node(tree, record.id, None, 0))
    db.commit()
    db.refresh(record)
    return get_tree(db, record.id)


def update_tree(db: Session, tree_id: int, tree: TagTree) -> TreeRecord | None:
    record = db.get(TreeRecord, tree_id)
    if record is None:
        return None

    # Updating is treated as replacing the submitted hierarchy. That keeps the
    # API simple and avoids trying to diff arbitrary recursive structures.
    for node in list(record.nodes):
        db.delete(node)

    db.flush()
    db.add(_to_node(tree, record.id, None, 0))
    db.commit()
    db.refresh(record)
    return get_tree(db, record.id)


def get_tree(db: Session, tree_id: int) -> TreeRecord | None:
    statement = (
        select(TreeRecord)
        .where(TreeRecord.id == tree_id)
        .options(selectinload(TreeRecord.nodes))
    )
    return db.scalar(statement)


def get_all_trees(db: Session) -> list[TreeRecord]:
    statement = (
        select(TreeRecord)
        .order_by(TreeRecord.created_at.asc(), TreeRecord.id.asc())
        .options(selectinload(TreeRecord.nodes))
    )
    return list(db.scalars(statement).all())


def serialize_record(record: TreeRecord) -> dict:
    root = next(node for node in record.nodes if node.parent_id is None)

    # FastAPI can serialize the Pydantic tree object while preserving the same
    # JSON shape used by the React UI.
    return {
        "id": record.id,
        "tree": _to_tree(root),
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }


def _to_node(tree: TagTree, tree_id: int, parent_id: int | None, position: int) -> TagNode:
    node = TagNode(
        tree_id=tree_id,
        parent_id=parent_id,
        position=position,
        name=tree.name,
        data=tree.data,
    )

    if tree.children is not None:
        # SQLAlchemy fills parent_id from the relationship after the parent node
        # is attached, so nested children can be created before a database flush.
        node.children = [
            _to_node(child, tree_id, None, child_position)
            for child_position, child in enumerate(tree.children)
        ]

    return node


def _to_tree(node: TagNode) -> TagTree:
    if node.children:
        # Sibling order matters for a visual tree, so the stored position is
        # applied every time the hierarchy is reconstructed.
        children = sorted(node.children, key=lambda child: child.position)
        return TagTree(
            name=node.name,
            children=[_to_tree(child) for child in children],
        )

    return TagTree(name=node.name, data=node.data or "")
