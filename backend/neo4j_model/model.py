from py2neo import *
from utls.valid import filter_malice


class Neo4jConnector:
    
    def __init__(self, profile: str, username: str, password: str, id: int = 0) -> None:
        self.graph = Graph(profile, name=username, password=password)
        self.occupy = False
        self.id = id
    
    def run(self, cypher: str, params: dict):
        r'''
        Run cypher command (must use something like `$param_name` to occupy position for params)
        >>> a = Neo4jConnector()
        >>> ret = a.run('match(a{name:$name})return a', {'name': 'sample'})
        '''
        for k, v in params.items():
            params[k] = filter_malice(v)

        return self.graph.run(cypher,params)
    