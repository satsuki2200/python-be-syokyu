import os
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.const import TodoItemStatusCode

from .models.item_model import ItemModel
from .models.list_model import ListModel

from fastapi import Depends
from .dependencies import get_db
from sqlalchemy.orm import Session

DEBUG = os.environ.get("DEBUG", "") == "true"

app = FastAPI(
    title="Python Backend Stations",
    debug=DEBUG,
)

if DEBUG:
    from debug_toolbar.middleware import DebugToolbarMiddleware

    # panelsに追加で表示するパネルを指定できる
    app.add_middleware(
        DebugToolbarMiddleware,
        panels=["app.database.SQLAlchemyPanel"],
    )


class NewTodoItem(BaseModel):
    """TODO項目新規作成時のスキーマ."""

    title: str = Field(title="Todo Item Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo Item Description", min_length=1, max_length=200)
    due_at: datetime | None = Field(default=None, title="Todo Item Due")


class UpdateTodoItem(BaseModel):
    """TODO項目更新時のスキーマ."""

    title: str | None = Field(default=None, title="Todo Item Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo Item Description", min_length=1, max_length=200)
    due_at: datetime | None = Field(default=None, title="Todo Item Due")
    complete: bool | None = Field(default=None, title="Set Todo Item status as completed")


class ResponseTodoItem(BaseModel):
    id: int
    todo_list_id: int
    title: str = Field(title="Todo Item Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo Item Description", min_length=1, max_length=200)
    status_code: TodoItemStatusCode = Field(title="Todo Status Code")
    due_at: datetime | None = Field(default=None, title="Todo Item Due")
    created_at: datetime = Field(title="datetime that the item was created")
    updated_at: datetime = Field(title="datetime that the item was updated")


class NewTodoList(BaseModel):
    """TODOリスト新規作成時のスキーマ."""

    title: str = Field(title="Todo List Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo List Description", min_length=1, max_length=200)


class UpdateTodoList(BaseModel):
    """TODOリスト更新時のスキーマ."""

    title: str | None = Field(default=None, title="Todo List Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo List Description", min_length=1, max_length=200)


class ResponseTodoList(BaseModel):
    """TODOリストのレスポンススキーマ."""

    id: int
    title: str = Field(title="Todo List Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo List Description", min_length=1, max_length=200)
    created_at: datetime = Field(title="datetime that the item was created")
    updated_at: datetime = Field(title="datetime that the item was updated")


@app.get("/echo", tags=["Hello"])
def get_hello(message: str, name: str):
    return {"Message": f"{message} {name}!"}

@app.get("/health", tags=["System"])
def get_health():
    return {"status": "ok"}

@app.get("/lists/{todo_list_id}", tags=["Todoリスト"])
async def get_todo_list(todo_list_id: int, session: Session = Depends(get_db)):
    db_item = session.query(ListModel).filter(ListModel.id == todo_list_id).first()
    return db_item

@app.post("/lists", response_model=ResponseTodoList, tags=["Todoリスト"])
async def post_todo_list(data: NewTodoList, session: Session = Depends(get_db)):
    new_db_item = ListModel(
        title=data.title,
        description=data.description,
    )
    session.add(new_db_item)
    session.commit()
    session.refresh(new_db_item)
    return new_db_item

@app.put("/lists/{todo_list_id}", response_model=ResponseTodoList, tags=["Todoリスト"])
async def put_todo_list(todo_list_id: int, data: UpdateTodoList, session: Session = Depends(get_db)):
    try:
        db_item = session.query(ListModel).filter(ListModel.id == todo_list_id).first()
        if db_item is None:
            # session.rollback()
            raise HTTPException(status_code=404, detail='Todo List Not Found')
        db_item.title = data.title
        db_item.description = data.description
        session.commit()


    finally:
        session.refresh(db_item)
        return db_item

@app.delete("/lists/{todo_list_id}", tags=["Todoリスト"])
async def delete_todo_list(todo_list_id: int, session: Session = Depends(get_db)):
    try:
        db_item = session.query(ListModel).filter(ListModel.id == todo_list_id).first()
        if db_item is None:
            raise HTTPException(status_code=404, detail='Todo List Not Found')
        session.delete(db_item)
        session.commit()
        session.refresh(db_item)
    except Exception as e:
        print(e)
        error = e
        session.rollback()
    finally:
        if error is not None:
            return error
        return {}

@app.get("/lists/{todo_list_id}/items/{todo_item_id}", tags=["Todo項目"])
def get_todo_item(todo_list_id: int, todo_item_id: int, session: Session = Depends(get_db)):
    db_item = session.query(ItemModel).filter(ItemModel.id == todo_item_id , ItemModel.todo_list_id == todo_list_id).first()
    return db_item

@app.post("/lists/{todo_list_id}/items", response_model=ResponseTodoItem, tags={"Todo項目"})
async def post_todo_item(todo_list_id: int, data: NewTodoItem, session: Session = Depends(get_db)):
    new_db_item = ItemModel(
        todo_list_id = todo_list_id,
        title = data.title,
        description = data.description,
        status_code = TodoItemStatusCode.NOT_COMPLETED.value,
        due_at = data.due_at,
    )
    session.add(new_db_item)
    session.commit()
    session.refresh(new_db_item)
    return new_db_item

@app.put("/lists/{todo_list_id}/items/{todo_item_id}", response_model=ResponseTodoItem, tags=["Todo項目"])
async def put_todo_item(todo_list_id: int, todo_item_id: int, data: UpdateTodoItem, session: Session = Depends(get_db)):
    try:
        db_list = session.query(ListModel).filter(ListModel.id == todo_list_id).first()
        if db_list is None:
            raise HTTPException(status_code=404, detail='Todo List Not Found')
        db_item = session.query(ItemModel).filter(ItemModel.id == todo_item_id , ItemModel.todo_list_id == todo_list_id).first()
        if db_item is None:
            raise HTTPException(status_code=404, detail='Todo Item Not Found')
        
        db_item.title = data.title
        db_item.description = data.description
        db_item.due_at = data.due_at
        if data.complete is False:
            db_item.status_code = TodoItemStatusCode.NOT_COMPLETED.value
        elif data.complete is True:
            db_item.status_code = TodoItemStatusCode.COMPLETED.value

        session.commit()

    except Exception as e:
        print(e)
        session.rollback()
    finally:
        session.refresh(db_item)
        return db_item

@app.delete("/lists/{todo_list_id}/items/{todo_item_id}", tags=["Todo項目"])
async def delete_todo_item(todo_list_id: int, todo_item_id: int, session: Session = Depends(get_db)):
    try:
        db_list = session.query(ListModel).filter(ListModel.id == todo_list_id).first()
        if db_list is None:
            raise HTTPException(status_code=404, detail='Todo List Not Found')
        db_item = session.query(ItemModel).filter(ItemModel.id == todo_item_id , ItemModel.todo_list_id == todo_list_id).first()
        if db_item is None:
            raise HTTPException(status_code=404, detail='Todo Item Not Found')
        session.delete(db_item)
        session.commit()
        session.refresh(db_item)
    except Exception as e:
        error = e
        print(e)
        session.rollback()
    finally:
        if error is not None:
            return error
        return {}

# @app.get("/plus")
# def plus(a: int, b: int):
#     """足し算"""
#     return (a + b)