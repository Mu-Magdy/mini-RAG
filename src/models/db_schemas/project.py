from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    id: Optional[ObjectId]=Field(None,alias="_id")
    project_id: str=Field(...,min_length=1)
    
    @validator("project_id")
    def validate_project_id(cls,v):
        if not v.isalnum():
            raise ValueError("Project ID must be alphanumeric")
        return v
      
    # this class config is used to convert the ObjectId to a string so that it can be used in pydantic models
    class Config:
        arbitrary_types_allowed=True
