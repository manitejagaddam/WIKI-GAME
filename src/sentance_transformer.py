from sentence_transformers import SentenceTransformer
import numpy as np

class GetSimilarWord:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def getSimilarWord(self, query, links):
        texts = [txt for txt, _ in links]

        query_emb = self.model.encode([query])          
        link_embs = self.model.encode(texts)            

        similarities = np.dot(link_embs, query_emb.T).flatten()
        
        best_idx = np.argmax(similarities)
        best_text, best_url = links[best_idx]

        return best_text, best_url, similarities[best_idx]
