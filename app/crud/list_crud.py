from fastapi import HTTPException
from app.models.list_model import ListModel

from ..schemas.list_schema import NewTodoList
from ..schemas.list_schema import UpdateTodoList

from sqlalchemy.orm import Session

def get_todo_lists(db: Session, page: int, per_page: int):
    db_lists = db.query(ListModel).offset((page - 1) * per_page).limit(per_page).all()
    # データが0件の場合は、空の配列を返却する。
    return db_lists

def get_todo_list(db: Session, todo_list_id: int):
    try:
        db_list = db.query(ListModel).filter(ListModel.id == todo_list_id).first()
        if not db_list:
            raise HTTPException(status_code=404, detail='Todo List Not Found')
        return db_list

    except Exception as e:
        db.rollback()
        raise e

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
    try:
        db_item = db.query(ListModel).filter(ListModel.id == todo_list_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail='Todo List Not Found')
        db_item.title = update_todo_list.title
        db_item.description = update_todo_list.description
        db.commit()
        db.refresh(db_item)
        return db_item
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise e
    
async def delete_todo_list(db: Session, todo_list_id: int):
    try:
        db_list = db.query(ListModel).filter(ListModel.id == todo_list_id).first()
        if not db_list:
            raise HTTPException(status_code=404, detail='Todo List Not Found')
        db.delete(db_list)
        db.commit()
        return {"status": True}
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise e