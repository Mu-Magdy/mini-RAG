from pydantic import BaseModel,Field,validator
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime
class Asset(BaseModel):
    id: Optional[ObjectId] = Field(default_factory=ObjectId,alias="_id")
    asset_projectid: ObjectId
    asset_type: str=Field(...,min_length=1)
    asset_name: str=Field(...,min_length=1)
    asset_size: int=Field(default=None, gt=0)
    asset_config:dict = Field(default=None)
    asset_pushed_at: datetime=Field(default=datetime.utcnow)


    class Config:
        arbitrary_types_allowed=True
        

    @classmethod
    def get_indexes(cls):
        return [
            {
            "key": [("asset_projectid", 1)],
            "name": "asset_projectid_index_1",
            "unique": False
            }, 
            {
            "key": [("asset_projectid", 1),("asset_name",1)],
            "name": "asset_project_id_name_index_1",
            "unique": True
            }
        ]