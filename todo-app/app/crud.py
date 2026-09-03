"""CRUD operations for Todo items."""
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.models import Todo


def get_todos(
    db: Session,
    completed: bool | None = None,
    priority: str | None = None,
    search: str | None = None,
    sort: str = "created_desc",
) -> list[Todo]:
    """Fetch todos with optional filtering and sorting."""
    stmt = select(Todo)

    if completed is not None:
        stmt = stmt.where(Todo.completed == completed)
    if priority is not None:
        stmt = stmt.where(Todo.priority == priority)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            (Todo.title.ilike(pattern)) | (Todo.description.ilike(pattern))
        )

    sort_map = {
        "created_desc": desc(Todo.created_at),
        "created_asc": asc(Todo.created_at),
        "priority_desc": desc(Todo.priority),
        "priority_asc": asc(Todo.priority),
        "title_asc": asc(Todo.title),
        "title_desc": desc(Todo.title),
    }
    order = sort_map.get(sort, desc(Todo.created_at))
    stmt = stmt.order_by(order)
    return list(db.scalars(stmt).all())


def get_todo(db: Session, todo_id: int) -> Todo | None:
    return db.get(Todo, todo_id)


def create_todo(db: Session, data: dict) -> Todo:
    todo = Todo(**data)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def update_todo(db: Session, todo_id: int, data: dict) -> Todo | None:
    todo = db.get(Todo, todo_id)
    if todo is None:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo


def delete_todo(db: Session, todo_id: int) -> bool:
    todo = db.get(Todo, todo_id)
    if todo is None:
        return False
    db.delete(todo)
    db.commit()
    return True


def toggle_todo(db: Session, todo_id: int) -> Todo | None:
    todo = db.get(Todo, todo_id)
    if todo is None:
        return None
    todo.completed = not todo.completed
    db.commit()
    db.refresh(todo)
    return todo


def clear_completed(db: Session) -> int:
    todos = list(db.scalars(select(Todo).where(Todo.completed == True)).all())
    count = len(todos)
    for todo in todos:
        db.delete(todo)
    db.commit()
    return count
