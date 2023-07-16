import openai
import numpy as np
import pandas as pd
from typing import List, Any
from redis import Redis
from redis.commands.search.field import VectorField, TextField, NumericField
from redis.commands.search.query import Query
from redis.commands.search import Search

from config import EMBEDDING_MODEL, PREFIX, VECTOR_FIELD_NAME

def create_redis_client()->Redis:
    '''Get a Redis Connection'''
    r =  Redis(host='localhost', port=6379, db=0, decode_responses=True)
    return r

def create_hnsw_index(redis_client:Redis, index_name:str, vector_field_name:str, vector_dimenions:int,distance_metric:str)->Any:
    '''Create a Redis index to store the data'''
    try: 
        redis_client.ft(index_name).info()
        print('Index already exists!')
    except Exception as e: 
        print(e)
        print('Index does not exists, start creating one ...')
        redis_client.ft(index_name).create_index([
            VectorField(
            vector_field_name, 
            'HNSW', 
            {'TYPE': 'FLOAT32', 
            'DIM':vector_dimenions, 
            'DISTANCE_METRIC': distance_metric
            }),
            TextField('file_name'),
            TextField('text_batch'),
            NumericField('text_batch_index')
            ])
    print('Index info: {}'.format(redis_client.ft(index_name).info()))
    index = redis_client.ft(index_name).info()
    return index

def load_vectors(client:Redis, input_list:List, vector_field_name:str=VECTOR_FIELD_NAME, prefix:str=PREFIX)->List:
    '''Create a Redis pipeline to load all the vectors and their metadata'''
    p = client.pipeline(transaction=False)
    for text in input_list:
        key = f"{prefix}:{text['id']}" 
        item_metadata = text['metadata']
        item_keywords_vector = np.array(text['vector'],dtype= 'float32').tobytes()
        item_metadata[vector_field_name]=item_keywords_vector
        p.hset(key,mapping=item_metadata)
    p.execute()

def query_redis(redis_conn:Redis, query:str, index_name:str, top_k=1)->Search:
    '''Make query to Redis'''
    embedded_query = np.array(openai.Embedding.create(
        input=query, 
        model=EMBEDDING_MODEL, 
    )['data'][0]['embedding'], dtype=np.float32).tobytes()
    
    q = Query(f'*=>[KNN {top_k} @{VECTOR_FIELD_NAME} $vec_param AS vector_score]')\
        .sort_by('vector_score').paging(0,top_k)\
        .return_fields('vector_score','filename','text_batch','batch_index')\
        .dialect(2) 
    params_dict = {"vec_param": embedded_query}
    results = redis_conn.ft(index_name).search(q, query_params = params_dict)
    return results

def get_redis_results(redis_conn:Redis, query:str, index_name:str)->List:
    '''Retrieve the most relavent documents from Redis'''
    query_results = query_redis(redis_conn, query, index_name)

    query_result_list = []
    for i, result in enumerate(query_results.docs): 
        result_order = i 
        text = result.text_batch
        filename = result.filename
        score = result.vector_score 
        query_result_list.append((result_order, text, score, filename))
    
    result_df = pd.DataFrame(query_result_list)
    result_df.columns = ['order', 'text', 'score', 'filename']
    return result_df