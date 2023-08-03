from neo4j_model.db_pool import NEO4j_POOL
from AK_Graph_Backend.settings import NEO_DB_POOL

NEO4j_POOL.initPool(**NEO_DB_POOL)