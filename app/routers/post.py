from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
import logging
import psycopg2
from psycopg2.extras import RealDictCursor # reveal col name
from .. import models, schemas, utils
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List
from sqlalchemy import func

router = APIRouter(tags=['Posts'])

@router.get("/posts", response_model = List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db), maxpost: int = 10):
    # cur.execute("""SELECT * FROM posts""")
    # posts = cur.fetchall()
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).order_by(models.Post.id.desc()).limit(maxpost).all()
    return posts

@router.get("/posts/latest", response_model = schemas.PostResponse)
def get_latest_post(db: Session = Depends(get_db)):
    # cur.execute("""SELECT * FROM posts ORDER BY posts.id DESC LIMIT 1""")
    # post = cur.fetchone()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).order_by(models.Post.id.desc()).first()
    
    return post

@router.get("/posts/{id}", response_model = schemas.PostResponse)
def get_post(id: int, db: Session = Depends(get_db)):
    # cur.execute("""SELECT * FROM posts WHERE posts.id = %s""", (str(id)))
    # getpost = cur.fetchone()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    return post

# function takes in a JWT token and verifies it with the help of utils.get_current_user dependency that calls the verify_access_token logic
@router.post("/posts", status_code=status.HTTP_201_CREATED, response_model = schemas.BasePostResponse)
def create_post(post: schemas.Post, db: Session = Depends(get_db), current_user = Depends(utils.get_current_user)):
    # cur.execute("""INSERT INTO posts(title, content, category, location, rating, published) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *;""",
    # (post.title, post.content, post.category, post.location, post.rating, post.published))
    # post = cur.fetchone()
    # conn.commit()
    post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user = Depends(utils.get_current_user)):
    # cur.execute("""DELETE FROM posts WHERE posts.id = %s RETURNING *""", (str(id)))
    # post = cur.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if not post:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.patch("/posts/{id}", response_model = schemas.BasePostResponse)
def update_post(id:int, updatepost: schemas.UpdatePost, db: Session = Depends(get_db), current_user = Depends(utils.get_current_user)):
    # post_dict = post.dict(exclude_unset=True)
    # updateval = "UPDATE posts SET "
    # for key, val in post_dict.items():
    #     # if attribute is not rating or published (i.e. string variable), include quotation marks
    #     if str(key) not in ["rating", "published"]:
    #         updateval += str(key) + " = '" + str(val) + "', "
    #     else:
    #         updateval += str(key) + " = " + str(val) + ", "
    # updateval = updateval[:-2] + " WHERE posts.id = %s RETURNING *"
    # print(updateval)
    # cur.execute(updateval, (str(id)))
    # post = cur.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    post_query.update(updatepost.dict(exclude_unset=True),synchronize_session=False)
    db.commit()
    
    return post