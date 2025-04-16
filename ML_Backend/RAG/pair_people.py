from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

model_name = "sentence-transformers/all-mpnet-base-v2"

# 1) Create embeddings using Hugging Face Sentence Transformer
print(f"[INFO] Using model: {model_name}")
embeddings = HuggingFaceEmbeddings(
    model_name=model_name, model_kwargs={"device": "cpu"}
)


def load_user_embeddings(
    persist_directory: str = "User_Embeddings",
    collection_name: str = "interests",
):
    """
    Returns a dict {user_id: embedding_vector} for each user.
    """
    # 1) Initialize the Chroma DB
    vectordb = Chroma(
        collection_name=collection_name,
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )

    # 2) The Chroma internal collection object
    collection = vectordb._collection  # private API, but handy for direct data

    # 3) Get all embeddings and metadata
    #    collection.get(...) can fetch embeddings, metadatas, and documents
    results = collection.get(include=["embeddings", "metadatas", "documents"])

    # 4) Convert into a user-friendly structure
    #    results["embeddings"] is a list of vectors
    #    results["metadatas"] is a list of dicts (like {"user_id": 123})
    #    results["ids"] are internal IDs
    user_id_to_embedding = {}
    for embedding, meta in zip(results["embeddings"], results["metadatas"]):
        user_id = meta.get("user_id")
        if user_id is not None:
            user_id_to_embedding[user_id] = embedding

    return user_id_to_embedding


import numpy as np
import networkx as nx


import numpy as np
import networkx as nx


def pair_users_by_similarity(user_id_to_embedding: dict, top_k=10):
    """
    Takes {user_id: embedding_vector} and returns the top-k pairs of users
    that have the highest similarity.
    """
    user_ids = list(user_id_to_embedding.keys())
    embeddings = [user_id_to_embedding[uid] for uid in user_ids]
    n = len(user_ids)

    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    # Create a list of (userA, userB, similarity)
    similarities = []
    for i in range(n):
        for j in range(i + 1, n):
            uid_i = user_ids[i]
            uid_j = user_ids[j]
            sim = cosine_similarity(embeddings[i], embeddings[j])
            similarities.append((uid_i, uid_j, sim))

    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[2], reverse=True)

    # Select the top-k pairs
    top_pairs = similarities[:top_k]

    return [(user1, user2) for user1, user2, _ in top_pairs]


def group_users_in_fours(user_id_to_embedding: dict):
    """
    Greedily form groups of 4 based on average similarity to each other.
    """
    user_ids = list(user_id_to_embedding.keys())
    embeddings = {uid: np.array(vec) for uid, vec in user_id_to_embedding.items()}

    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    groups = []

    while len(user_ids) >= 4:
        # 1) Pick the first user
        anchor_user = user_ids[0]
        anchor_emb = embeddings[anchor_user]

        # 2) Compute similarity with all others
        sims = []
        for other in user_ids[1:]:
            sim = cosine_similarity(anchor_emb, embeddings[other])
            sims.append((other, sim))

        # 3) Sort by similarity descending
        sims.sort(key=lambda x: x[1], reverse=True)

        # 4) Take top 3
        top3 = [anchor_user] + [uid for (uid, _) in sims[:3]]
        groups.append(top3)

        # 5) Remove these 4 from user_ids
        for uid in top3:
            user_ids.remove(uid)

    # If leftover users remain (less than 4), they remain unmatched
    return groups


# if __name__ == "__main__":
#     user_id_to_embedding = load_user_embeddings()
#     print(f"Loaded {len(user_id_to_embedding)} user embeddings.")
#     # print(user_id_to_embedding)

#     pairs = pair_users_by_similarity(user_id_to_embedding)
#     for u1, u2 in pairs:
#         print(f"Paired {u1} with {u2}")

if __name__ == "__main__":
    user_id_to_embedding = load_user_embeddings()
    print(f"Loaded {len(user_id_to_embedding)} user embeddings.")
    groups_of_4 = group_users_in_fours(user_id_to_embedding)
    for idx, group in enumerate(groups_of_4, start=1):
        print(f"Group {idx}:", group)
