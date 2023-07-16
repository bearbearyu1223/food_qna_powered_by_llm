# Food QnA Chatbot Demo
## Set Up Local Virtual Environment
* Step 1: Install Miniconda on MacOS, see instruction [here](https://docs.conda.io/en/latest/miniconda.html). 
* Step 2: Create a default conda env with Python 3.9: 
``conda create --name food_qna_app python=3.9 -y``
* Step 3: Activate the conda env created above: 
``conda activate food_qna_app``
* Step 4: Install first set of required libraries in the conda env: 
``` 
pip3 install -r requirements.txt
```
* Step 5: Deactivate the conda env when you are done (note: you need activate this virtual env to work on the app)
```
conda deactivate 
```
## Set Up Open AI Secrete for Local Dev 
`OPENAI_API_KEY` will be needed when calling the OpenAI API endpoint for generating embeddings for the documents, so do recommend exporting `OPENAI_API_KEY` as an enviroment variable on your local dev machine; also, we will need create a `secrets.toml` file and add the `OPENAI_API_KEY` there, so the streamlit app can pick up the API key when send requests to OpenAI endpoint during runtime. 
* Step 1: Export `OPENAI_API_KEY` as an enviroment variable on your local dev machine
* Step 2: Create `.streamlit` directory under the root repo 
```
cd food_qna_chatbot_demo 
mkdir .streamlit
```
* Step 3: Create `secrets.toml` file under `.streamlit` directory and add your `OPENAI_API_KEY` there 
```
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY_HERE>
```
* Step 4: To reduce the risk of accidentally committing your secrets to your repo, add `.streamlit` to your `.gitignore` file. 
```
echo ".streamlit/" >> .gitignore
```
## Set up the Redis Database on your local dev machine 
* Step 1: [Install Docker Desktop on Mac](https://docs.docker.com/desktop/install/mac-install/), and start the docker desktop. 
* Step 2: We're going to use Redis as our database for both document contents and the vector embeddings. You will need the full Redis Stack to enable use of Redisearch, which is the module that allows semantic search - more detail is in the docs for [Redis Stack](https://redis.io/docs/stack/get-started/install/docker/). Run the following command in your terminal to start the docker container:
```
docker run -d --name redis-stack -p 127.0.0.1:6379:6379 -p 8001:8001 redis/redis-stack:latest
```
* Step 3: Initiate a Redis connection and create a Hierarchical Navigable Small World (HNSW) index for semantic search using a recipe book which can be found under the directory `cook_book_data`
```
python build_knowledge_base.py
```
If the recipe book is indexed succefully into the DB, you should expect the following info printed out in the console:
```
===
Number of documents indexed in the DB: 144
``` 
## Run the APP
In your terminal, run the App by
```
streamlit run food_qna_app.py
```
You can start asking questions related to food preparation and cooking, and also some follow up questions. See screenshot below. 
| Original Content                                  | Chat History                                     |
| --------------------------------------------------|--------------------------------------------------|
| ![Original Content](picture/original_content.png) | ![Chat History](picture/chat_history_1.png)      |


| Original Content                       |Chat History - first turn               |Chat History - follow up                |
|----------------------------------------|----------------------------------------|----------------------------------------|
| ![Original Content](picture/original_content.png)  | ![Chat History](picture/chat_history_1.png)  | ![Chat History](picture/chat_history_2.png)  |