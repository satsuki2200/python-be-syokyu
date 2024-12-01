from fastapi import APIRouter, Depends
from app.dependencies import get_db
from sqlalchemy.orm import Session

from ..schemas.item_schema import ResponseTodoItem
from ..schemas.item_schema import NewTodoItem
from ..schemas.item_schema import UpdateTodoItem
import app.crud.item_crud as item_crud

router = APIRouter(
    prefix="/lists/{todo_list_id}/items",
    tags=["Todo項目"]
)

# テストを通すために実装
@router.get("/")

@router.get("/{todo_item_id}")
def get_todo_item(todo_list_id: int, todo_item_id: int, session: Session = Depends(get_db)):
    return item_crud.get_todo_item(session, todo_list_id, todo_item_id)

@router.post("/", response_model=ResponseTodoItem)
async def post_todo_item(todo_list_id: int, data: NewTodoItem, session: Session = Depends(get_db)):
    return item_crud.post_todo_item(session, todo_list_id, data)

@router.put("/{todo_item_id}", response_model=ResponseTodoItem)
async def put_todo_item(todo_list_id: int, todo_item_id: int, data: UpdateTodoItem, session: Session = Depends(get_db)):
    return item_crud.update_todo_item(session, todo_list_id, todo_item_id, data)
    
@router.delete("/{todo_item_id}")
async def delete_todo_item(todo_list_id: int, todo_item_id: int, session: Session = Depends(get_db)):
    return item_crud.delete_todo_item(session, todo_list_id, todo_item_id)
