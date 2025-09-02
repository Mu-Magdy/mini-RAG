import json
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import PGVectorDistanceMethodEnums, PGVectorIndexTypeEnums, PGVectorTableSchemaEnums,DistanceMethodEnums
import logging
from typing import List
from models.db_schemes import RetrievedDocument
from sqlalchemy.sql import text as sql_text

class PGVectorProvider(VectorDBInterface):

    def __init__(self, db_client, default_vector_size: int=786, 
                 distance_method: str=None,
                 index_threshold: int=100):
        self.db_client = db_client
        self.default_vector_size = default_vector_size
        self.index_threshold = index_threshold
        
        if distance_method == DistanceMethodEnums.COSINE.value:
            distance_method = PGVectorDistanceMethodEnums.COSINE.value
        elif distance_method == DistanceMethodEnums.DOT.value:
            distance_method = PGVectorDistanceMethodEnums.DOT.value
        
        self.pgvector_table_prefix = PGVectorTableSchemaEnums._PREFIX.value
        self.distance_method = distance_method
        self.logger = logging.getLogger("uvicorn")
        self.default_index_name=lambda collection_name:f"{collection_name}_vector_idx"

    
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
            list_tbl=sql_text(f"Select * from pg_tables where tablename = :collection_name")
            result = await session.execute(list_tbl, {"collection_name": collection_name})
            record = result.scalar_one_or_none()
        return record 
      
    async def list_all_collections(self) -> List:
        record=[]
        async with self.db_client() as session:
          async with session.begin():
            list_tbl=sql_text(f"Select tablename from pg_tables where tablename like '{self.pgvector_table_prefix}%'")
            result = await session.execute(list_tbl)
            record = result.scalars().all()
        return record
        
    async def get_collection_info(self, collection_name: str) -> dict:
        async with self.db_client() as session:
          async with session.begin():
            table_info_sql=sql_text(f"Select schemaname, tablename, tableowner,tablespace, hasindexes from pg_tables where tablename = :collection_name")
            count_sql=sql_text(f"Select count(*) from {collection_name}")
            result = await session.execute(table_info_sql, {"collection_name": collection_name})
            record_count = await session.execute(count_sql)
            
            table_data = result.fetchone()
            if not table_data:
                return None
     
        return {
          "table_info":{
            "schema_name":table_data.schemaname,
            "table_name":table_data.tablename,
            "table_owner":table_data.tableowner,
            "table_space":table_data.tablespace,
            "has_indexes":table_data.hasindexes
            },
          "record_count":record_count.scalar_one() 
        }
        
    async def delete_collection(self, collection_name: str):
        async with self.db_client() as session:
          async with session.begin():
            self.logger.info(f"Deleting collection: {collection_name}")
             
            drop_tbl=sql_text(f"Drop table if exists {collection_name}")
            await session.execute(drop_tbl)
          await session.commit()
        return True    
      
          
    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if do_reset:
            _ = await self.delete_collection(collection_name=collection_name)
          
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.info(f"Creating collection: {collection_name}")
            async with self.db_client() as session:
              async with session.begin():
                create_tbl=sql_text(f"Create table {collection_name} ("
                                    f"{PGVectorTableSchemaEnums.ID.value} bigserial primary key, "
                                    f"{PGVectorTableSchemaEnums.TEXT.value} text, "
                                    f"{PGVectorTableSchemaEnums.VECTOR.value} vector({embedding_size}), "
                                    f"{PGVectorTableSchemaEnums.METADATA.value} jsonb default \'{{}}\', "
                                    f"{PGVectorTableSchemaEnums.CHUNK_ID.value} integer, "
                                    f"FOREIGN KEY ({PGVectorTableSchemaEnums.CHUNK_ID.value}) REFERENCES chunks(chunk_id))"
                                    
                                    )
                await session.execute(create_tbl)
                await session.commit()
            return True
        return False
      
    async def is_index_existed(self, collection_name: str)->bool:
      index_name=self.default_index_name(collection_name)
      async with self.db_client() as session:
        async with session.begin():
          index_info=sql_text(f"Select 1 from pg_indexes where tablename=:collection_name AND indexname = :index_name")
          result = await session.execute(index_info, {"collection_name": collection_name, "index_name": index_name})
          record = result.scalar_one_or_none()
      return record is not None


    async def create_vector_index(self, collection_name: str,
                                  index_type:str=PGVectorIndexTypeEnums.HNSW.value):
      is_index_existed = await self.is_index_existed(collection_name=collection_name)
      if is_index_existed:
        return False
      
      async with self.db_client() as session:
        async with session.begin():
          count_sql=sql_text(f"Select count(*) from {collection_name}")
          result = await session.execute(count_sql)
          records_count = result.scalar_one()
          if records_count < self.index_threshold:
            return False

          self.logger.info(f"Creating index {self.default_index_name(collection_name)} on {collection_name} using {index_type}")
         
          index_name=self.default_index_name(collection_name)
          create_index=sql_text(f"Create index {index_name} on {collection_name} using {index_type} ({PGVectorTableSchemaEnums.VECTOR.value} {self.distance_method})")
          await session.execute(create_index)          

          self.logger.info(f"Finished creating index {self.default_index_name(collection_name)} on {collection_name} using {index_type}")

    async def reset_vector_index(self, collection_name: str,
                                 index_type:str=PGVectorIndexTypeEnums.HNSW.value):
      index_name=self.default_index_name(collection_name)
      async with self.db_client() as session:
        async with session.begin():
          drop_index=sql_text(f"Drop index if exists {index_name}")
          await session.execute(drop_index)
        await session.commit()
      return await self.create_vector_index(collection_name=collection_name,
                                            index_type=index_type) 
      
    async def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict = None, record_id: str = None):
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        if not record_id:
          self.logger.error(f"Can not insert new record without chunk_id:{collection_name}")
          return False

        async with self.db_client() as session:
          async with session.begin():
            
            insert_tbl=sql_text(f"Insert into  {collection_name} (
                                {PGVectorTableSchemaEnums.TEXT.value}, {PGVectorTableSchemaEnums.VECTOR.value}, {PGVectorTableSchemaEnums.METADATA.value}, {PGVectorTableSchemaEnums.CHUNK_ID.value})
                                values (:text, :vector, :metadata, :chunk_id)")
            metadata_json=json.dumps(metadata,ensure_ascii=False) if metadata else "{}"
            
            await session.execute(insert_tbl, {"text": text,
                                               "vector": '[' + ','.join(str(v) for v in vector) + ']',
                                               "metadata": metadata_json,
                                               "chunk_id": record_id})
            await session.commit()
        await self.create_vector_index(collection_name=collection_name)
            
        return True
      
    async def insert_many(self, collection_name: str, texts: list, 
                          vectors: list, metadata: list = None, 
                          record_ids: list = None, batch_size: int = 50):
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        
        if len(vectors) != len(record_ids):
            self.logger.error(f"Length of vectors and record_ids must be the same: {collection_name}")
            return False
        
        if metadata is None or len(metadata) == 0:
            metadata = [None] * len(texts)

            
        async with self.db_client() as session:
          async with session.begin():
            for i in range(0, len(texts), batch_size):
                batch_end = i + batch_size

                batch_texts = texts[i:batch_end]
                batch_vectors = vectors[i:batch_end]
                batch_metadata = metadata[i:batch_end]
                batch_record_ids = record_ids[i:batch_end]
                
                values = []
                for _text, _vector, _metadata, _record_id in zip(batch_texts, batch_vectors, batch_metadata, batch_record_ids):
                    metadata_json=json.dumps(_metadata,ensure_ascii=False) if _metadata else "{}"
                    values.append({"text":_text,
                                   "vector":'[' + ','.join(str(v) for v in _vector) + ']',
                                   "metadata":metadata_json,
                                  "chunk_id":_record_id})
                    
                insert_tbl=sql_text(f"Insert into  {collection_name} (
                                    {PGVectorTableSchemaEnums.TEXT.value},
                                    {PGVectorTableSchemaEnums.VECTOR.value},
                                    {PGVectorTableSchemaEnums.METADATA.value}
                                    , {PGVectorTableSchemaEnums.CHUNK_ID.value})
                                    values (:text, :vector, :metadata, :chunk_id)")
                await session.execute(insert_tbl, values)
                await session.commit()
                
          await self.create_vector_index(collection_name=collection_name)
          return True

    async def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Can not search in non-existed collection: {collection_name}")
            return False
        
        vector = '[' + ','.join(str(v) for v in vector) + ']'
        
        async with self.db_client() as session:
          async with session.begin():
            search_tbl=sql_text(f"Select {PGVectorTableSchemaEnums.TEXT.value} as text,
                                1 - {PGVectorTableSchemaEnums.VECTOR.value} <=> vector as score,
                                {PGVectorTableSchemaEnums.METADATA.value} as metadata
                                from {collection_name} ORDER BY score DESC 
                                limit {limit}")
            result = await session.execute(search_tbl, {"vector": vector})
            records = result.fetchall()
            
        return [
            RetrievedDocument(**{
                "text": record.text,
                "score": record.score,
            })
            for record in records
        ]