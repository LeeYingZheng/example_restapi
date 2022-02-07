from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
import logging
import psycopg2
from psycopg2.extras import RealDictCursor # reveal col name
from .. import models, schemas, utils
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List
from sqlalchemy.exc import IntegrityError

router = APIRouter(tags=['Users'])

@router.post("/users/create", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.User, db: Session = Depends(get_db)):
    try:
        user.password = utils.hash(user.password)
        user = models.User(**user.dict())
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    except IntegrityError:
        db.rollback()
        email = db.query(models.User).filter(models.User.email == user.email).first()
        username = db.query(models.User).filter(models.User.username == user.username).first()
        if email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use. Please use another email address.")
        elif username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already in use. Please use another username.")
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User cannot be created. Please check your credentials again.")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unknown logic not handled by application")

# view own profile
@router.get("/users/profile", response_model=schemas.UserResponse)
def get_profile(db: Session = Depends(get_db), current_user = Depends(utils.get_current_user)):

    user = db.query(models.User).filter(models.User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user

# view own posts, include drafts
@router.get("/users/profile/posts", response_model = List[schemas.PostResponse])
def get_profile_posts(db: Session = Depends(get_db), current_user = Depends(utils.get_current_user)):

    posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    return posts

@router.patch("/users/profile", response_model=schemas.UpdateUserResponse)
def update_user_profile(updateuser: schemas.UpdateUser, db: Session = Depends(get_db), current_user = Depends(utils.get_current_user)):

    user = db.query(models.User).filter(models.User.id == current_user.id)

    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.update(updateuser.dict(exclude_unset=True),synchronize_session=False)
    db.commit()
    
    return user.first()

# view other users' profile
@router.get("/users/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    return user

# view other users' published posts, exclude drafts
@router.get("/users/{id}/posts", response_model = List[schemas.PostResponse])
def get_user_posts(id: int, db: Session = Depends(get_db)):

    posts = db.query(models.Post).filter(models.Post.owner_id == id, models.Post.published == True).all() # TO DO: include published = true filter
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    return posts

@router.post("/users/pass", response_model=schemas.UpdateUserResponse)
def change_password(updateuser: schemas.UpdateUserPassword, db: Session = Depends(get_db), current_user = Depends(utils.get_current_user)):

    user = db.query(models.User).filter(models.User.id == current_user.id)
 
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") 

    newpass = utils.hash(updateuser.password)
    user.update({models.User.password:newpass},synchronize_session=False)
    db.commit()
    
    return user.first()

@router.post("/users/delete", response_model=schemas.UpdateUserResponse)
def delete_account(db: Session = Depends(get_db), current_user = Depends(utils.get_current_user)):

    user = db.query(models.User).filter(models.User.id == current_user.id)
 
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") 

    user.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

