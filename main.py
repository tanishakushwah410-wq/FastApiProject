from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import engine, get_db
import model
import schemas
from auth import create_token, verify_token

model.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Home Route
@app.get("/")
def home():
    return {"message": "Blog API Started"}


# Login
@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    if form.username != "admin" or form.password != "admin123":
        raise HTTPException(status_code=401, detail="Wrong username or password")
    return {
        "access_token": create_token({"user": form.username}),
        "token_type": "bearer",
    }


# Create blog (protected)
@app.post("/blogs", response_model=schemas.BlogResponse)
def create_blog(
    blog: schemas.BlogCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token),
):
    new_blog = model.Blog(title=blog.title, content=blog.content)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


# Get all blogs (pagination + search)
@app.get("/blogs", response_model=schemas.BlogListResponse)
def get_blogs(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=5, ge=1, le=100),
    search: str = Query(default=""),
    db: Session = Depends(get_db),
):
    query = db.query(model.Blog)

    if search:
        query = query.filter(model.Blog.title.ilike(f"%{search}%"))

    total = query.count()
    start = (page - 1) * limit
    blogs = query.order_by(model.Blog.id).offset(start).limit(limit).all()

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "data": blogs,
    }


# Get one blog
@app.get("/blogs/{blog_id}", response_model=schemas.BlogResponse)
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(model.Blog).filter(model.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog


# Update blog (protected)
@app.put("/blogs/{blog_id}", response_model=schemas.BlogResponse)
def update_blog(
    blog_id: int,
    updated: schemas.BlogCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token),
):
    blog = db.query(model.Blog).filter(model.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    blog.title = updated.title
    blog.content = updated.content
    db.commit()
    db.refresh(blog)
    return blog


# Delete blog (protected)
@app.delete("/blogs/{blog_id}")
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token),
):
    blog = db.query(model.Blog).filter(model.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    db.delete(blog)
    db.commit()
    return {"message": "Blog deleted"}