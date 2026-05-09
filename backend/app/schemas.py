from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TagTree(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    children: list["TagTree"] | None = None
    data: str | None = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name cannot be empty")
        return value

    @model_validator(mode="after")
    def validate_shape(self) -> Self:
        has_children = self.children is not None
        has_data = self.data is not None

        if has_children == has_data:
            raise ValueError("each tag must contain either children or data")
        if self.children is not None and len(self.children) == 0:
            raise ValueError("children cannot be empty")

        return self


class TreeIn(BaseModel):
    tree: TagTree


class TreeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tree: TagTree
    created_at: datetime
    updated_at: datetime

