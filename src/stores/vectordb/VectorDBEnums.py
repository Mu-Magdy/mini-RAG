from enum import Enum

class VectorDBEnums(Enum):
    QDRANT = "QDRANT"
<<<<<<< HEAD
    PGVECTOR = "PGVECTOR"
=======
>>>>>>> d73c391 (Merge pull request #1 from Mu-Magdy/feat-semantic-search)

class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"
<<<<<<< HEAD
    
class PGVectorDistanceMethodEnums(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_l2_ops"
    
class PGVectorIndexTypeEnums(Enum):
    HNSW = "hnsw"
    IVFFLAT = "ivfflat"

class PGVectorTableSchemaEnums(Enum):
    ID = "id"
    TEXT = "text"
    VECTOR = "vector"
    CHUNK_ID = "chunk_id"
    METADATA = "metadata"
    _PREFIX = "pgvector"
=======
>>>>>>> d73c391 (Merge pull request #1 from Mu-Magdy/feat-semantic-search)
