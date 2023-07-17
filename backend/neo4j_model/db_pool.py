from neo4j_model.model import Neo4jConnector


class DB_POOL:
    r'''
    This is the Neo4j DB Pool
    '''
    POOL = []
    Free_Stack = []
    State = []
    
    '''state of dbconnector'''
    FREE = 0
    BUSY = 1
    
    @staticmethod
    def initPool(profile: str, username: str, password: str, size: int = 1):
        print('initialize for db pool')
        for i in range(size):
            # initialize for pool and free stack
            DB_POOL.POOL.append(Neo4jConnector(profile, username, password, i))
            DB_POOL.Free_Stack.append(i)
            DB_POOL.State.append(DB_POOL.FREE)
        print('initialize successfully')
    
    def getConnect() -> Neo4jConnector:
        r'''
        return an unoccupied `instance` of Neo4jConnector,
        
        if there has no spare Neo4jConnector, return `None`
        '''
        # get rend id
        if (len(DB_POOL.Free_Stack) != 0):
            rend_id = DB_POOL.Free_Stack.pop()
        else:
            return None
        
        # set busy state
        DB_POOL.State[rend_id] = DB_POOL.BUSY
        
        return DB_POOL.POOL[rend_id]
    
    def free(connector: Neo4jConnector):
        r'''
        free Neo4jConnector source
        '''
        if DB_POOL.State[connector.id] == DB_POOL.BUSY:
            DB_POOL.State[connector.id] = DB_POOL.FREE
            DB_POOL.Free_Stack.append(connector.id)