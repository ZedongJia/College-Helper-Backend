from neo4j_model.model import Neo4jConnector


class NEO4j_POOL:
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
            NEO4j_POOL.POOL.append(Neo4jConnector(profile, username, password, i))
            NEO4j_POOL.Free_Stack.append(i)
            NEO4j_POOL.State.append(NEO4j_POOL.FREE)
        print('initialize successfully')
    
    def getConnect() -> Neo4jConnector:
        r'''
        return an unoccupied `instance` of Neo4jConnector,
        
        if there has no spare Neo4jConnector, return `None`
        '''
        # get rend id
        if (len(NEO4j_POOL.Free_Stack) != 0):
            rend_id = NEO4j_POOL.Free_Stack.pop()
        else:
            return None
        
        # set busy state
        NEO4j_POOL.State[rend_id] = NEO4j_POOL.BUSY
        
        return NEO4j_POOL.POOL[rend_id]
    
    def free(connector: Neo4jConnector):
        r'''
        free Neo4jConnector source
        '''
        if NEO4j_POOL.State[connector.id] == NEO4j_POOL.BUSY:
            NEO4j_POOL.State[connector.id] = NEO4j_POOL.FREE
            NEO4j_POOL.Free_Stack.append(connector.id)