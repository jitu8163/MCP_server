import os
import time
import uuid
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION")
VECTOR_SIZE = 384  # e5-small-v2

def get_qdrant_client():
    if not QDRANT_URL or not QDRANT_API_KEY:
        raise ValueError("QDRANT_URL or QDRANT_API_KEY missing in .env")

    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=60.0
    )

def create_collection_if_not_exists():
    client = get_qdrant_client()
    collections = [c.name for c in client.get_collections().collections]

    if COLLECTION_NAME not in collections:
        print(f"Creating Qdrant collection: {COLLECTION_NAME}")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")

def make_deterministic_uuid(text: str) -> str:
    # Same text -> same UUID (deterministic, collision-resistant)
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, text))

class QdrantStore:
    def __init__(self, ensure_collection: bool = False):
        self.client = get_qdrant_client()
        if ensure_collection:
            create_collection_if_not_exists()

    def add(self, texts, embeddings, metadatas, batch_size=100):
        total = len(texts)
        print(f"Uploading {total} vectors to Qdrant in batches of {batch_size}...")

        for i in range(0, total, batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_vectors = embeddings[i:i+batch_size]
            batch_meta = metadatas[i:i+batch_size]

            points = []
            for text, vector, meta in zip(batch_texts, batch_vectors, batch_meta):
                payload = {"text": text}
                payload.update(meta)

                point_id = make_deterministic_uuid(text)

                points.append({
                    "id": point_id,
                    "vector": vector,
                    "payload": payload
                })

            for attempt in range(3):
                try:
                    self.client.upsert(
                        collection_name=COLLECTION_NAME,
                        points=points
                    )
                    print(f"Uploaded batch {(i // batch_size) + 1} / {(total + batch_size - 1) // batch_size}")
                    break
                except Exception as e:
                    print(f"⚠ Batch {(i // batch_size) + 1} failed (attempt {attempt+1}/3): {e}")
                    time.sleep(3)
                    if attempt == 2:
                        raise

    def search(self, query_vector, top_k=5):
        try:
            # New Qdrant API (v1.7+)
            res = self.client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,
                limit=top_k,
                with_payload=True
            )
            results = res.points
        except AttributeError:
            # Old Qdrant API fallback
            results = self.client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_vector,
                limit=top_k,
                with_payload=True
            )

        return [
            {
                "id": str(r.id),
                "score": float(r.score),
                "payload": r.payload
            }
            for r in results
        ]





# import os
# import time
# import uuid
# from dotenv import load_dotenv
# from qdrant_client import QdrantClient
# from qdrant_client.models import VectorParams, Distance

# load_dotenv()

# QDRANT_URL = os.getenv("QDRANT_URL")
# QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
# COLLECTION_NAME = os.getenv("QDRANT_COLLECTION")
# VECTOR_SIZE = 384  # e5-small-v2

# def get_qdrant_client():
#     if not QDRANT_URL or not QDRANT_API_KEY:
#         raise ValueError("QDRANT_URL or QDRANT_API_KEY missing in .env")

#     return QdrantClient(
#         url=QDRANT_URL,
#         api_key=QDRANT_API_KEY,
#         timeout=60.0
#     )

# def create_collection_if_not_exists():
#     client = get_qdrant_client()
#     collections = [c.name for c in client.get_collections().collections]

#     if COLLECTION_NAME not in collections:
#         print(f"Creating Qdrant collection: {COLLECTION_NAME}")
#         client.create_collection(
#             collection_name=COLLECTION_NAME,
#             vectors_config=VectorParams(
#                 size=VECTOR_SIZE,
#                 distance=Distance.COSINE
#             )
#         )
#     else:
#         print(f"Collection '{COLLECTION_NAME}' already exists.")

# def make_deterministic_uuid(text: str) -> str:
#     # Same text -> same UUID (deterministic, collision-resistant)
#     return str(uuid.uuid5(uuid.NAMESPACE_DNS, text))

# class QdrantStore:
#     def __init__(self):
#         self.client = get_qdrant_client()
#         create_collection_if_not_exists()

#     def add(self, texts, embeddings, metadatas, batch_size=100):
#         total = len(texts)
#         print(f"Uploading {total} vectors to Qdrant in batches of {batch_size}...")

#         for i in range(0, total, batch_size):
#             batch_texts = texts[i:i+batch_size]
#             batch_vectors = embeddings[i:i+batch_size]
#             batch_meta = metadatas[i:i+batch_size]

#             points = []
#             for text, vector, meta in zip(batch_texts, batch_vectors, batch_meta):
#                 payload = {"text": text}
#                 payload.update(meta)

#                 point_id = make_deterministic_uuid(text)

#                 points.append({
#                     "id": point_id,
#                     "vector": vector,
#                     "payload": payload
#                 })

#             for attempt in range(3):
#                 try:
#                     self.client.upsert(
#                         collection_name=COLLECTION_NAME,
#                         points=points
#                     )
#                     print(f"Uploaded batch {(i // batch_size) + 1} / {(total + batch_size - 1) // batch_size}")
#                     break
#                 except Exception as e:
#                     print(f"⚠ Batch {(i // batch_size) + 1} failed (attempt {attempt+1}/3): {e}")
#                     time.sleep(3)
#                     if attempt == 2:
#                         raise

#     def search(self, query_vector, top_k=5):
#         results = self.client.search(
#             collection_name=COLLECTION_NAME,
#             query_vector=query_vector,
#             limit=top_k,
#             with_payload=True
#         )

#         return [
#             {
#                 "id": str(r.id),
#                 "score": float(r.score),
#                 "payload": r.payload
#             }
#             for r in results
#         ]
