"""API routes for the todo app."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import TodoCreate, TodoOut, TodoUpdate

router = APIRouter(prefix="/api/todos", tags=["todos"])


@router.get("", response_model=list[TodoOut])
def list_todos(
    completed: bool | None = None,
    priority: str | None = None,
    search: str | None = None,
    sort: str = "created_desc",
    db: Session = Depends(get_db),
) -> list[TodoOut]:
    todos = crud.get_todos(db, completed=completed, priority=priority, search=search, sort=sort)
    return [TodoOut.model_validate(t) for t in todos]


@router.get("/stats")
def todo_stats(db: Session = Depends(get_db)) -> dict:
    todos = crud.get_todos(db)
    total = len(todos)
    completed = sum(1 for t in todos if t.completed)
    by_priority = {"low": 0, "medium": 0, "high": 0}
    for t in todos:
        by_priority[t.priority] = by_priority.get(t.priority, 0) + 1
    return {
        "total": total,
        "completed": completed,
        "active": total - completed,
        "by_priority": by_priority,
    }


@router.post("", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(todo_in: TodoCreate, db: Session = Depends(get_db)) -> TodoOut:
    todo = crud.create_todo(db, todo_in.model_dump())
    return TodoOut.model_validate(todo)


@router.get("/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int, db: Session = Depends(get_db)) -> TodoOut:
    todo = crud.get_todo(db, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return TodoOut.model_validate(todo)


@router.patch("/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, todo_in: TodoUpdate, db: Session = Depends(get_db)) -> TodoOut:
    todo = crud.update_todo(db, todo_id, todo_in.model_dump(exclude_unset=True))
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return TodoOut.model_validate(todo)


@router.post("/{todo_id}/toggle", response_model=TodoOut)
def toggle_todo(todo_id: int, db: Session = Depends(get_db)) -> TodoOut:
    todo = crud.toggle_todo(db, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return TodoOut.model_validate(todo)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Session = Depends(get_db)) -> None:
    deleted = crud.delete_todo(db, todo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Todo not found")


@router.delete("", status_code=status.HTTP_200_OK)
def clear_completed_todos(db: Session = Depends(get_db)) -> dict:
    count = crud.clear_completed(db)
    return {"cleared": count}
