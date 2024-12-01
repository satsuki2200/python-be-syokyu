from fastapi import HTTPException

from app.const import TodoItemStatusCode

from app.models.item_model import ItemModel
from app.models.list_model import ListModel

from ..schemas.item_schema import NewTodoItem
from ..schemas.item_schema import UpdateTodoItem

from fastapi import Depends
from sqlalchemy.orm import Session

def get_todo_items(db: Session, todo_list_id: int):
    db_items = db.query(ItemModel).filter(ItemModel.todo_list_id == todo_list_id).all()
    return db_items

def get_todo_item(db:Session, todo_list_id: int, todo_item_id: int):
    db_item = db.query(ItemModel).filter(ItemModel.id == todo_item_id , ItemModel.todo_list_id == todo_list_id).first()
    return db_item

def post_todo_item(db: Session, todo_list_id: int, data: NewTodoItem):
    new_db_item = ItemModel(
        todo_list_id = todo_list_id,
        title = data.title,
        description = data.description,
        status_code = TodoItemStatusCode.NOT_COMPLETED.value,
        due_at = data.due_at,
    )
    db.add(new_db_item)
    db.commit()
    db.refresh(new_db_item)
    return new_db_item

def update_todo_item(db: Session, todo_list_id: int, todo_item_id: int, data: UpdateTodoItem):
    try:
        db_list = db.query(ListModel).filter(ListModel.id == todo_list_id).first()
        if db_list is None:
            raise HTTPException(status_code=404, detail='Todo List Not Found')
        db_item = db.query(ItemModel).filter(ItemModel.id == todo_item_id , ItemModel.todo_list_id == todo_list_id).first()
        if db_item is None:
            raise HTTPException(status_code=404, detail='Todo Item Not Found')
        
        db_item.title = data.title
        db_item.description = data.description
        db_item.due_at = data.due_at
        if data.complete is False:
            db_item.status_code = TodoItemStatusCode.NOT_COMPLETED.value
        elif data.complete is True:
            db_item.status_code = TodoItemStatusCode.COMPLETED.value

        db.commit()

    except Exception as e:
        db.rollback()
    finally:
        db.refresh(db_item)
        return db_item
    
def delete_todo_item(db: Session, todo_list_id: int, todo_item_id: int):
    status = None
    try:
        db_list = db.query(ListModel).filter(ListModel.id == todo_list_id).first()
        if db_list is None:
            raise HTTPException(status_code=404, detail='Todo List Not Found')
        db_item = db.query(ItemModel).filter(ItemModel.id == todo_item_id , ItemModel.todo_list_id == todo_list_id).first()
        if db_item is None:
            raise HTTPException(status_code=404, detail='Todo Item Not Found')
        db.delete(db_item)
        db.commit()
        db.refresh(db_item)
        status = HTTPException(status_code=200, detail="Success")
    except Exception as e:
        status = e
        db.rollback()
    finally:
        return HTTPException(status_code=200, detail="Success")