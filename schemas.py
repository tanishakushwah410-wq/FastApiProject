from pydantic import BaseModel

#Input schema:-
class BlogCreate(BaseModel):
    title: str
    content: str

#Output Schema:-
class BlogResponse(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True

#Pagination Response Schema:-
class BlogListResponse(BaseModel):
    page: int
    limit: int
    total: int
    data: list[BlogResponse]