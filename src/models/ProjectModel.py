from .BaseDataModel import BaseDataModel
from .db_schemas import Project
from .enums.DataBaseEnum import DataBaseEnum

class ProjectModel(BaseDataModel):
  def __init__(self,db_client:object):
    super().__init__(db_client)
    self.collection=self.db_client[DataBaseEnum.COLLECTION_PROJECTS_NAME.value]

  async def create_project(self,project:Project):
    result=await self.collection.insert_one(project.dict(by_alias=True,exclude_unset=True))
    project._id=str(result.inserted_id)
    return project
  
  async def get_project_or_create_one(self,project_id:str):
    record=await self.collection.find_one({"project_id":project_id})
    if record is None:
      project=Project(project_id=project_id)
      project=await self.create_project(project)
      return project
    
    else:
      return Project(**record) 
  
  async def get_all_projects(self,page:int=1,page_size:int=10):
    total_docs=await self.collection.count_documents({})
    total_pages=total_docs//page_size
    if total_docs%page_size!=0:
      total_pages+=1
    skip=(page-1)*page_size
    cursor=self.collection.find().skip(skip).limit(page_size)
    projects=[]
    async for project in cursor:
      projects.append(Project(**project))
      
    return projects,total_pages
