from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import PGVectorDistanceMethodEnums, PGVectorIndexTypeEnums, PGVectorTableSchemaEnums
import logging
from typing import List
from models.db_schemes import RetrievedDocument
from sqlalchemy.sql import text as sql_text

class PGVectorProvider(VectorDBInterface):

    def __init__(self, db_client, default_vector_size: int=786, distance_method: str=None):
        self.db_client = db_client
        self.default_vector_size = default_vector_size
        self.distance_method = distance_method
        
        self.pgvector_table_prefix = PGVectorTableSchemaEnums._PREFIX.value

        self.logger = logging.getLogger("uvicorn")

    async def connect(self):
        async with self.db_client() as session:
          async with session.begin():
            await session.execute(sql_text(f"CREATE EXTENSION IF NOT EXISTS vector"))
            
          await session.commit()
          
          
    async def disconnect(self):
        pass
    
    async def is_collection_existed(self, collection_name: str) -> bool:
        record=None
        async with self.db_client() as session:
          async with session.begin():
            list_tbl=sql_text("Select * from pg_tables where tablename = :collection_name")
            result = await session.execute(list_tbl, {"collection_name": collection_name})
            record = result.scalar_one_or_none()
        return record 
      
    async def list_all_collections(self) -> List:
        record=[]
        async with self.db_client() as session:
          async with session.begin():
            list_tbl=sql_text("Select tablename from pg_tables where tablename like :prefix")
            result = await session.execute(list_tbl, {"prefix": f"{self.pgvector_table_prefix}%"})
            record = result.scalars().all()
        return record
        
    async def get_collection_info(self, collection_name: str) -> dict:
        async with self.db_client() as session:
          async with session.begin():
            table_info_sql=sql_text("Select schemaname, tablename, tableowner,tablespace, hasindexes from pg_tables where tablename = :collection_name")
            count_sql=sql_text("Select count(*) from :collection_name")
            result = await session.execute(table_info_sql, {"collection_name": collection_name})
            count_result = await session.execute(count_sql, {"collection_name": collection_name})
            
            table_data = result.fetchone()
            if not table_data:
                return None
     
        return {
          "table_info":dict(table_data),
          "count":count_result
        }
        
    