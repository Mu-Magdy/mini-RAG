<<<<<<< HEAD
from sqlalchemy import func
from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum
from sqlalchemy.future import select

=======
from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum
>>>>>>> d73c391 (Merge pull request #1 from Mu-Magdy/feat-semantic-search)

class ProjectModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
<<<<<<< HEAD
        self.db_client = db_client
=======
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
>>>>>>> d73c391 (Merge pull request #1 from Mu-Magdy/feat-semantic-search)

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
<<<<<<< HEAD

        return instance

    async def create_project(self, project: Project):
        async with self.db_client.begin() as session:
            async with session.begin():
                session.add(project)
            await session.commit()
            await session.refresh(project)

        return project
        

    async def get_project_or_create_one(self, project_id: str):
        async with self.db_client() as session:
            async with session.begin():
                query = await session.execute(select(Project).where(Project.project_id == project_id))
                project = query.scalar_one_or_none()

                if project is None:
                    project_record = Project(
                        project_id=project_id
                        )

                    project=await self.create_project(project=project_record)

                    return project

                return project

       
    async def get_all_projects(self, page: int=1, page_size: int=10):

        async with self.db_client() as session:
            async with session.begin():
                total_documents = await session.execute(select(
                        func.count(Project.project_id)
                    )
                )
                total_documents = total_documents.scalar_one()
                
                total_pages = total_documents // page_size
                if total_documents % page_size > 0:
                    total_pages += 1

                query = select(Project).offset((page-1) * page_size).limit(page_size)
                
                projects = await session.execute(query)
                projects = projects.scalars().all()

                return projects, total_pages

        
=======
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )


    async def create_project(self, project: Project):

        result = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))
        project.id = result.inserted_id

        return project

    async def get_project_or_create_one(self, project_id: str):

        record = await self.collection.find_one({
            "project_id": project_id
        })

        if record is None:
            # create new project
            project = Project(project_id=project_id)
            project = await self.create_project(project=project)

            return project
        
        return Project(**record)

    async def get_all_projects(self, page: int=1, page_size: int=10):

        # count total number of documents
        total_documents = await self.collection.count_documents({})

        # calculate total number of pages
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1

        cursor = self.collection.find().skip( (page-1) * page_size ).limit(page_size)
        projects = []
        async for document in cursor:
            projects.append(
                Project(**document)
            )

        return projects, total_pages
>>>>>>> d73c391 (Merge pull request #1 from Mu-Magdy/feat-semantic-search)
