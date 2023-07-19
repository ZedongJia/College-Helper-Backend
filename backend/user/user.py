
class User:
    
    def __init__(self, info_tuple):
        '''
        ID bigint AI
        nick_name varchar(50)
        account varchar(50) PK
        password varchar(50) PK
        image mediumblob
        telephone varchar(20)
        gender varchar(2)
        email varchar(50)
        QQ varchar(20)
        weChat
        '''
        if info_tuple != None:
            keys = ['ID','nickname','account','password','image','telephone','gender','email','QQ','weChat']
            self.info = { keys[i]:info_tuple[i] if info_tuple[i] != None else '' for i in range(len(keys))}
        else:
            self.info = None

    def __str__(self):
        return str(self.info)
    
    def hasUser(self):
        return self.info != None
