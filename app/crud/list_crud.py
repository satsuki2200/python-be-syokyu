from fastapi import HTTPException
from app.models.list_model import ListModel

from ..schemas.list_schema import NewTodoList
from ..schemas.list_schema import UpdateTodoList

from sqlalchemy.orm import Session

def get_todo_list(db: Session, todo_list_id: int):
    db_list = db.query(ListModel).filter(ListModel.id == todo_list_id).first()
    return db_list

def create_todo_list(db: Session, data: NewTodoList):
    new_db_list = ListModel(
        title=data.title,
        description=data.description,
    )
    db.add(new_db_list)
    db.commit()
    db.refresh(new_db_list)
    return new_db_list

def update_todo_list(db: Session, todo_list_id: int, update_todo_list: UpdateTodoList):
    error = None
    try:
        db_item = db.query(ListModel).filter(ListModel.id == todo_list_id).first()
        if db_item is None:
            raise HTTPException(status_code=404, detail='Todo List Not Found')
        db_item.title = update_todo_list.title
        db_item.description = update_todo_list.description
        db.commit()

    except Exception as e:
        error = e
        db.rollback()
    
    finally:
        if error is not None:
            return error
        db.refresh(db_item)
        return db_item
    
async def delete_todo_list(db: Session, todo_list_id: int):
    status = None
    try:
        db_list = db.query(ListModel).filter(ListModel.id == todo_list_id).first()
        if db_list is None:
            raise HTTPException(status_code=404, detail='Todo List Not Found')
        db.delete(db_list)
        db.commit()
        db.refresh(db_list)
        status = {"status": True}

    except Exception as e:
        status = e
        db.rollback()

    finally:
        return HTTPException(status_code=200, detail=status)