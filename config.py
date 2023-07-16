COMPLETION_MODEL = 'text-davinci-003'
EMBEDDING_MODEL = 'text-embedding-ada-002'
CHAT_MODEL = 'gpt-3.5-turbo'
TOKENIZER = 'cl100k_base'
EMBEDDING_CTX_LENGTH = 8191 # the max embedding length accepted by "text-embedding-ada-002" 
VECTOR_DIM = 1536 # the max embedding vector dim accepted by openAI
VECTOR_FIELD_NAME='content_vector'
PREFIX = 'cook-book'  
INDEX_NAME = "book-index"
DISTANCE_METRIC = 'COSINE'