from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship


class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="user.id", description="작성자 ID")
    title: str = Field(description="게시글 제목")
    content: str = Field(description="게시글 내용")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = Field(default=None)

    # 관계
    author: Optional["User"] = Relationship(back_populates="posts")


class PostCreate(SQLModel):
    title: str
    content: str


class PostRead(SQLModel):
    id: int
    author_id: int
    title: str
    content: str
    created_at: datetime
