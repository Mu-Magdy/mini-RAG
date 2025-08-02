from .BaseDataModel import BaseDataModel
from .db_schemas import Project
from .enums.DataBaseEnum import DataBaseEnum

class ProjectModel(BaseDataModel):
  def __init__(self,db_client:object):
    super().__init__(db_client)
    self.collection=self.db_client[DataBaseEnum.COLLECTION_PROJECTS_NAME.value]
    
  
  @classmethod
  async def create_instance(cls,db_client:object):
    instance=cls(db_client)
    await instance.init_collection()
    return instance
  
  async def init_collection(self): 
    all_collections=await self.db_client.list_collection_names()
    
    if DataBaseEnum.COLLECTION_PROJECTS_NAME.value not in all_collections:
      self.collection=await self.db_client.create_collection(DataBaseEnum.COLLECTION_PROJECTS_NAME.value)
      indexes=Project.get_indexes()
      for index in indexes:
        await self.collection.create_index(index["key"],name=index["name"],unique=index["unique"])


  async def create_project(self,project:Project):
    result=await self.collection.insert_one(project.dict(by_alias=True,exclude_unset=True))
    project.id=str(result.inserted_id)
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
