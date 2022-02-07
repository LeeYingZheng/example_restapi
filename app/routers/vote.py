from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(tags=['Vote'])

@router.post("/vote", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), current_user = Depends(utils.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id==vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        
    vote_query = db.query(models.Vote).filter(models.Vote.post_id==vote.post_id, models.Vote.user_id == current_user.id)
    
    # vote up + vote not in database
    if vote.dir and not vote_query.first():
        db.add(models.Vote(post_id=vote.post_id,user_id=current_user.id))
        db.commit()
        return {"response": "vote added successfully"}
        
    # downvote on existing vote
    elif not vote.dir and vote_query.first():
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"response": "vote removed successfully"}
    
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Voting conflict")