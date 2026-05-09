from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class TreeRecord(Base):
    __tablename__ = "tree_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    nodes: Mapped[list["TagNode"]] = relationship(
        back_populates="tree",
        cascade="all, delete-orphan",
        order_by="TagNode.position",
    )


class TagNode(Base):
    __tablename__ = "tag_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tree_id: Mapped[int] = mapped_column(
        ForeignKey("tree_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("tag_nodes.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    data: Mapped[str | None] = mapped_column(Text, nullable=True)

    tree: Mapped[TreeRecord] = relationship(back_populates="nodes")
    parent: Mapped["TagNode | None"] = relationship(
        back_populates="children",
        remote_side=[id],
    )
    children: Mapped[list["TagNode"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="TagNode.position",
    )

