from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .models import TagNode, TreeRecord
from .schemas import TagTree


def create_tree(db: Session, tree: TagTree) -> TreeRecord:
    record = TreeRecord()
    db.add(record)
    db.flush()

    db.add(_to_node(tree, record.id, None, 0))
    db.commit()
    db.refresh(record)
    return get_tree(db, record.id)


def update_tree(db: Session, tree_id: int, tree: TagTree) -> TreeRecord | None:
    record = db.get(TreeRecord, tree_id)
    if record is None:
        return None

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
        node.children = [
            _to_node(child, tree_id, None, child_position)
            for child_position, child in enumerate(tree.children)
        ]

    return node


def _to_tree(node: TagNode) -> TagTree:
    if node.children:
        children = sorted(node.children, key=lambda child: child.position)
        return TagTree(
            name=node.name,
            children=[_to_tree(child) for child in children],
        )

    return TagTree(name=node.name, data=node.data or "")

