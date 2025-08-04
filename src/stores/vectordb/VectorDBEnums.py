from enum import Enum

class VectorDBEnums(Enum):
    FAISS = "faiss"
    CHROMA = "chroma"
    PINECONE = "pinecone"
    QDRANT = "qdrant"
    MILVUS = "milvus"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"


class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    CHEBYSHEV = "chebyshev"
    MINKOWSKI = "minkowski"
    DOT = "dot"
    HAMMING = "hamming"
    JACCARD = "jaccard"