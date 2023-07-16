import os
import requests
import numpy as np
import re

from redis import Redis
from redis.commands.search.query import Query
from redis.commands.search.field import (
    TextField, 
    VectorField, 
    NumericField
)
from redis.commands.search.indexDefinition import (
    IndexDefinition, 
    IndexType
)
from redis_db import create_redis_client, create_hnsw_index, load_vectors
from config import VECTOR_DIM, VECTOR_FIELD_NAME, PREFIX, INDEX_NAME, DISTANCE_METRIC
from pdf_preprocessor import extract_content_from_pdfs
from generate_embedding import len_safe_get_embedding

if __name__=='__main__': 
    redis_client = create_redis_client()
    index = create_hnsw_index(redis_client=redis_client, index_name=INDEX_NAME, vector_field_name=VECTOR_FIELD_NAME,\
            vector_dimenions=VECTOR_DIM, distance_metric=DISTANCE_METRIC)

    if index: 
        try:
            vectors = []
            book_dir = os.path.join(os.curdir,'cook_book_data')
            books = extract_content_from_pdfs(book_dir=book_dir)
            for book_title, book in books.items():
                book_title_cleaned = re.sub('[^a-zA-Z0-9]', '_', book_title)
                for page_number, page in book.items():
                    if page['len_of_raw_text']>0:
                        raw_text = page['raw_text']
                        file_name = book_title_cleaned + '_' + page_number
                        batched_texts, batched_embeddings = len_safe_get_embedding(text=raw_text)
                        i = 0
                        for texts, embeddings in zip(batched_texts, batched_embeddings): 
                            id = file_name + '_' + 'batch_'+ str(i)
                            vectors.append(
                                {
                                    'id' : id, 
                                    'vector': embeddings, 
                                    'metadata': {
                                        'filename': file_name, 
                                        'text_batch': texts, 
                                        'batch_index': i
                                    }
                                }
                            )
                            i = i + 1
            try: 
                load_vectors(redis_client, vectors)
            except Exception as e: 
                print(e)
        except Exception as e: 
            print(e)
        print("=========")
        print("Number of documents indexed in the DB: {}".format(redis_client.ft(INDEX_NAME).info()['num_docs']))