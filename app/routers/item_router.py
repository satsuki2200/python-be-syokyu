from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_db
from sqlalchemy.orm import Session

from ..schemas.item_schema import ResponseTodoItem
from ..schemas.item_schema import NewTodoItem
from ..schemas.item_schema import UpdateTodoItem
import app.crud.list_crud as list_crud
import app.crud.item_crud as item_crud

router = APIRouter(
    prefix="/lists/{todo_list_id}/items",
    tags=["Todo項目"]
)

@router.get("/")
def get_todo_items(todo_list_id: int, page: int, per_page: int, session: Session = Depends(get_db)):
    return item_crud.get_todo_items(session, todo_list_id, page, per_page)

@router.get("/{todo_item_id}")
def get_todo_item(todo_list_id: int, todo_item_id: int, session: Session = Depends(get_db)):
    db_item = item_crud.get_todo_item(session, todo_list_id, todo_item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Todo Item Not Found")
    return db_item

@router.post("/", response_model=ResponseTodoItem)
async def post_todo_item(todo_list_id: int, data: NewTodoItem, session: Session = Depends(get_db)):
    # パスパラメータで指定したtodo_list_idが存在するかどうか確認
    db_list = list_crud.get_todo_list(session, todo_list_id)
    if db_list is None:
        raise HTTPException(status_code=404, detail='Todo List Not Found')
    db_item = item_crud.post_todo_item(session, todo_list_id, data)
    return db_item

@router.put("/{todo_item_id}", response_model=ResponseTodoItem)
async def put_todo_item(todo_list_id: int, todo_item_id: int, data: UpdateTodoItem, session: Session = Depends(get_db)):
    db_item = item_crud.update_todo_item(session, todo_list_id, todo_item_id, data)
    if db_item is None:
        raise HTTPException(status_code=404, detail='Todo Item Not Found')
    return db_item
    
@router.delete("/{todo_item_id}")
async def delete_todo_item(todo_list_id: int, todo_item_id: int, session: Session = Depends(get_db)):
    return await item_crud.delete_todo_item(session, todo_list_id, todo_item_id)
