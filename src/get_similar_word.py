from sentence_transformers import SentenceTransformer
import numpy as np
import logging

class GetSimilarWord:
    def __init__(self):
        logging.info("Loading SentenceTransformer model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        logging.info("Model loaded.")

    def getSimilarWord(self, query, links):
        if not links:
            logging.warning("Link list is empty. Cannot compute similarity.")
            return None, None, None

        # Filter out empty or None text items
        clean_links = [(txt, url) for txt, url in links if txt and txt.strip()]
        
        if not clean_links:
            logging.warning("All link texts are empty after filtering.")
            return None, None, None

        texts = [txt for txt, _ in clean_links]

        logging.info(f"Encoding {len(texts)} link texts...")
        query_emb = self.model.encode([query])
        link_embs = self.model.encode(texts)

        # Cosine similarity (fast and simple)
        similarities = np.dot(link_embs, query_emb.T).flatten()

        best_idx = np.argmax(similarities)
        best_text, best_url = clean_links[best_idx]
        best_score = similarities[best_idx]

        logging.info(f"Best match: '{best_text}' ({best_score:.4f})")

        return best_text, best_url, best_score
