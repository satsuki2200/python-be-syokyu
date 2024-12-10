from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_db
from sqlalchemy.orm import Session

from ..schemas.list_schema import ResponseTodoList
from ..schemas.list_schema import NewTodoList
from ..schemas.list_schema import UpdateTodoList
import app.crud.list_crud as list_crud

router = APIRouter(
    prefix="/lists",
    tags=["Todoリスト"]
)

@router.get("/")
def get_todo_lists(page: int, per_page: int, session: Session = Depends(get_db)):
    return list_crud.get_todo_lists(session, page, per_page)

@router.get("/{todo_list_id}")
async def get_todo_list(todo_list_id: int, session: Session = Depends(get_db)):
    db_list = list_crud.get_todo_list(session, todo_list_id)
    if db_list is None:
        raise HTTPException(status_code=404, detail='Todo List Not Found')
    return db_list

@router.post("/", response_model=ResponseTodoList)
async def post_todo_list(data: NewTodoList, session: Session = Depends(get_db)):
    return list_crud.create_todo_list(session, data)

@router.put("/{todo_list_id}", response_model=ResponseTodoList)
async def put_todo_list(todo_list_id: int, data: UpdateTodoList, session: Session = Depends(get_db)):
    db_list = list_crud.update_todo_list(session, todo_list_id, data)
    if db_list is None:
        raise HTTPException(status_code=404, detail='Todo List Not Found')
    return db_list

@router.delete("/{todo_list_id}")
async def delete_todo_list(todo_list_id: int, session: Session = Depends(get_db)):
   return await list_crud.delete_todo_list(session, todo_list_id)
    