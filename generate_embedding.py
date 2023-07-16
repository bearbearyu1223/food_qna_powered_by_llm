from typing import List, Union, Iterable, Tuple
from itertools import islice
from numpy import array, average
import pandas as pd 
import numpy as np 
import tiktoken
import os
import openai

from config import EMBEDDING_MODEL, EMBEDDING_CTX_LENGTH, TOKENIZER
from redis_db import load_vectors

def truncate_text_tokens(text:str, tokenizer:str=TOKENIZER, max_tokens:str=EMBEDDING_CTX_LENGTH)->List[int]:
    '''Truncate text into smaller chunks to have max_tokens according to the given tokenizer'''
    text = text.encode('ascii', 'replace')
    text = text.decode()
    text = text.replace('  ', '').replace('\n', ' ')
    encoding = tiktoken.get_encoding(tokenizer)
    return encoding.encode(text)[:max_tokens]


def generate_batches(iterable:Iterable, batch_size:int)->Iterable: 
    '''Batch data into tuples of size n
       example: 
        batched('abcdefg', 3) --> abc def g
    '''
    if batch_size < 1: 
        raise ValueError('batch_size must be an integer larger or equal than one')
    it = iter(iterable)
    while (batch := tuple(islice(it, batch_size))):
        yield batch 

def batched_tokens(text:str, batch_size:int): 
    text = text.encode('ascii', 'replace')
    text = text.decode()
    text = text.replace('  ', '').replace('\n', ' ')
    encoding = tiktoken.encoding_for_model(EMBEDDING_MODEL)
    tokens = encoding.encode(text)
    batch_iterator = generate_batches(tokens, batch_size)
    yield from batch_iterator


def _get_embedding(text_or_tokens: Union[str, List[str]], model:str=EMBEDDING_MODEL)->List[float]:
    '''Get embedding for the input text or the input list of tokens'''
    embedding = openai.Embedding.create(input=text_or_tokens, model=model)['data'][0]['embedding']
    return embedding

def len_safe_get_embedding(text:str, model=EMBEDDING_MODEL, max_tokens=EMBEDDING_CTX_LENGTH, encoding_name=TOKENIZER, average=False)->List:
    '''Get embedding for long text in a safe way without exceeding the max token lengths accepted by OpenAI models'''
    batched_embeddings = []
    batched_texts = []
    batch_sizes = []
    for batch in batched_tokens(text=text,batch_size=max_tokens):
        batched_embeddings.append(_get_embedding(batch, model=model))
        tokenizer = tiktoken.encoding_for_model(EMBEDDING_MODEL)
        batched_texts.append(tokenizer.decode(batch))
        batch_sizes.append(len(batch))

    if average: 
        # average the embeddings along the row direction
        batched_embeddings = np.average(batched_embeddings, axis=0, weights=batch_sizes) 
        # normalized the embeddings
        batched_embeddings = batched_embeddings / np.linalg.norm(batched_embeddings) 
        batched_embeddings = batched_embeddings.tolist()
    return batched_texts, batched_embeddings


def handle_file_string(file, tokenizer, redis_conn, text_embedding_field, index_name):
    '''
    Process a file string by cleaning it up, creating embeddings and uploading them to Redis
    Args:
        file(tuple): a tuple containing the filename and file body string
        tokenizer: the tokenizer object used for encoding and decoding text
        redis_conn: the redis connecion object 
        text_embedding_field(str): the field in Redis where the text embeddings will be stored
        index_name: the name of the index or identifier for the embeddings  
    Returns:
    Raises:
    '''
    pass

if __name__=='__main__': 
    openai.api_key = os.getenv("OPENAI_API_KEY")
    text = "keep the beat\u2122\nrecipes\ndeliciously healthy dinners\n"
    batched_texts, batched_embeddings = len_safe_get_embedding(text=text, max_tokens=3)
    # print(batched_texts)

    batched_texts, avg_batched_embeddings = len_safe_get_embedding(text=text, max_tokens=3, average=True)
    # print(avg_batched_embeddings)