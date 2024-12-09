from fastapi import APIRouter, Depends
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
def get_todo_lists(session: Session = Depends(get_db)):
    return list_crud.get_todo_lists(session)

@router.get("/{todo_list_id}")
async def get_todo_list(todo_list_id: int, session: Session = Depends(get_db)):
    return list_crud.get_todo_list(session, todo_list_id)

@router.post("/", response_model=ResponseTodoList)
async def post_todo_list(data: NewTodoList, session: Session = Depends(get_db)):
    return list_crud.create_todo_list(session, data)

@router.put("/{todo_list_id}", response_model=ResponseTodoList)
async def put_todo_list(todo_list_id: int, data: UpdateTodoList, session: Session = Depends(get_db)):
    return list_crud.update_todo_list(session, todo_list_id, data)

# 404はうまくいった 200がおかしい
# 200が想定されるとき、500が返ってくるけど、リストの削除はされてる
@router.delete("/{todo_list_id}")
async def delete_todo_list(todo_list_id: int, session: Session = Depends(get_db)):
   return await list_crud.delete_todo_list(session, todo_list_id)
    