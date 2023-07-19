import json
import random
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.db import connection, Error
from user.entities.user import User
import datetime
from utls.encrypt import encrypt
from utls.valid import Validate

# from neo4j_model.db_pool import DB_POOL
# Create your views here.

@require_http_methods(["GET", "POST"])
def account(request):
    r'''
    登录接口, 注册接口
    '''
    with connection.cursor() as cursor:
        try:
            if request.method == 'GET':

                # 获取基本信息
                account = request.GET.get('account', None)
                password = request.GET.get('password', None)
                password = encrypt(password)

                # 查询
                cursor.execute('select * from user where account=%s and password=%s',
                               (account, password))
                userInfo = cursor.fetchone()

                # 获取userInfo的Json
                user = User(userInfo)
                
                if not user.hasUser():
                    raise Error

                # 设置cookie 和 session
                response = HttpResponse(json.dumps(user.info, ensure_ascii=False), content_type='application/json')
                validate = Validate(str(user.info['ID']), user.info['account'], request, response)
                validate.sign()
                return response
            else:
                # 获取基本信息
                account = request.POST.get('account', None)
                password = request.POST.get('password', None)
                password = encrypt(password)
                # 插入
                cursor.execute('insert into user values(null, %s, %s, %s, null, null, "unknown", null, null, null)',
                               (account, account, password))
                return HttpResponse(200, content_type='application/json')
        except Error as e:
            return HttpResponse(400, content_type='application/json')

@require_http_methods(['GET'])
def state(request):
    # 前端发送的true不是True
    if (request.GET.get('logout') == 'true'):
        response = HttpResponse(200, content_type='application/json')
        Validate.drop(request, response)
        return response
    else:
        # 验证是否有效
        valid = Validate.valid(request)
        if valid:
            return HttpResponse(200, content_type='application/json')
        else:
            return HttpResponse(400, content_type='application/json')


@require_http_methods(['GET'])
def verify(request):
    length = 6
    verification = []
    for _ in range(length):
        verification.append(str(random.randint(0,9)))
    return HttpResponse(''.join(verification), content_type='application/json')

# 根据用户ID 获取、修改用户信息
def UserInfo(request):
    if request.method == 'GET':
        account_id = request.GET.get('id', None)
        if account_id == None:
            return HttpResponse(400, content_type='application/json')
        with connection.cursor() as cursor:
            try:
                cursor.execute('select * from user where ID = %s' % account_id)
                userInfo = cursor.fetchall()
                user = User(userInfo)
                response = HttpResponse(str(user), content_type='application/json')
                return response
            except Error as e:
                return HttpResponse(400, content_type='application/json')
    if request.method == 'POST':
        new_info = request.POST.copy() 
        if new_info == None:
            return HttpResponse(400, content_type='application/json')
        # new_info['password'] = User.encode(new_info['password'])
        with connection.cursor() as cursor:
            try:
                for i in new_info:
                    if i != 'ID':
                        cursor.execute("update user set %s = '%s' where ID = %s;" % (i, new_info[i], new_info['ID']))
                return HttpResponse(200, content_type='application/json')
            except:
                return HttpResponse(400, content_type='application/json')
        
# 根据用户ID 获取、修改privacy信息
def PrivacyInfo(request):
    if request.method == 'GET':
        account_id = request.GET.get('id', None)
        if account_id == None:
            return HttpResponse(400, content_type='application/json')
        with connection.cursor() as cursor:
            try:
                cursor.execute('select * from privacy where user_ID = %s;' % account_id)
                privacyInfo = cursor.fetchall()
                # 转化成字典数组
                keys = ['user_ID', 'telephone_priv', 'gender_priv', 'email_priv', 'QQ_priv', 'weChat_priv']
                '''
                这里你去新建一个privacy类, 仿照user进行处理,文件夹在entities下
                '''
                privacy = toDictList(keys, privacyInfo)
                return HttpResponse(json.dumps(privacy), content_type='application/json')
            except Error as e:
                return HttpResponse(400, content_type='application/json')
            
    if request.method == 'POST':
        new_info = request.POST
        if new_info == None:
            return HttpResponse(400, content_type='application/json')
        with connection.cursor() as cursor:
            try:
                for i in new_info:
                    if i != 'user_ID':
                        cursor.execute("update privacy set %s = '%s' where user_ID = %s;" % (i, new_info[i], new_info['user_ID']))
                return HttpResponse(200, content_type='application/json')
            except:
                return HttpResponse(400, content_type='application/json')
    
# 根据用户ID 返回对应private为true的信息字段
@require_http_methods(['GET'])
def getTruePrivacy(request):
    account_id = request.GET.get('id', None)
    if account_id == None:
        return HttpResponse(400, content_type='application/json')
    with connection.cursor() as cursor:
        try:
            cursor.execute('select * from privacy where user_ID = %s;' % account_id)
            privacyInfo = cursor.fetchall()[0]
            cursor.execute("select column_name from information_schema.columns where table_name = 'privacy'")
            keys = cursor.fetchall()
            key = []
            for i in range(len(privacyInfo)):
                if(privacyInfo[i] == 'true'):
                    key.append(keys[i])
            return HttpResponse(json.dumps(key), content_type='application/json')
        except Error as e:
            return HttpResponse(400, content_type='application/json')

# 根据用户ID 获取、删除历史记录
def BrowseInfo(request):
    # 获取历史记录
    if request.method == 'GET':
        account_id = request.GET.get('id', None)
        if account_id == None:
            return HttpResponse(400, content_type='application/json')
        with connection.cursor() as cursor:
            try:
                cursor.execute("select time, type, content from browsing_history where isHistory = 'true' and user_ID = %s order by time desc;" % account_id)
                BrowseHistory = cursor.fetchall()
                '''
                这里也是
                '''
                keys = ['time', 'type', 'content']
                browseInfo = toDictList(keys, BrowseHistory)
                return HttpResponse(json.dumps(browseInfo, default=str), content_type='application/json')
            except Error as e:
                return HttpResponse(400, content_type='application/json')
    # 删除历史记录
    if request.method == 'POST':
        info = request.GET    #  time、type、user_ID
        if info == None:
            return HttpResponse(400, content_type='application/json')

        with connection.cursor() as cursor:
            try:
                cursor.execute("update browsing_history set isHistory = 'false' where time = '%s' and type = '%s' and user_ID = %s;" % (info['time'], info['type'], info['user_ID']))
                return HttpResponse(200, content_type='application/json')
            except:
                return HttpResponse(400, content_type='application/json')
    

# 根据用户ID 获取、删除收藏记录
def CollectedInfo(request):
    # 获取收藏记录
    if request.method == 'GET':
        info = request.GET    #  user_ID
        print(info['user_ID'])
        if info == None:
            return HttpResponse(400, content_type='application/json')

        with connection.cursor() as cursor:
            try:
                cursor.execute("select time, type, content from browsing_history where isCollected = 'true' and user_ID = %s order by time desc;" % (info['user_ID']))
                CollectedInfo = cursor.fetchall()
                # 转化成字典数组
                keys = ['time', 'type', 'content']
                '''
                这里也是
                '''
                collectedInfo = toDictList(keys, CollectedInfo)
                return HttpResponse(json.dumps(collectedInfo, default=str), content_type='application/json')
            except Error as e:
                return HttpResponse(400, content_type='application/json')
    # 删除收藏记录
    if request.method == 'POST':
        info = request.GET    #  time、type、user_ID
        if info == None:
            return HttpResponse(400, content_type='application/json')

        with connection.cursor() as cursor:
            try:
                cursor.execute("update browsing_history set isCollected = 'false' where time = '%s' and type = '%s' and user_ID = %s;" % (info['time'], info['type'], info['user_ID']))
                return HttpResponse(200, content_type='application/json')
            except:
                return HttpResponse(400, content_type='application/json')
    
        
# 根据ID1和ID2获取聊天记录
@require_http_methods(['GET'])
def getMessageList(request):
    ID_info = request.GET    # user1_ID  user2_ID
    if ID_info == None:
        return HttpResponse(400, content_type='application/json')

    with connection.cursor() as cursor:
        try:
            cursor.execute('select ID from dialogue where user1_ID = %s and user2_ID = %s' % (ID_info['user1_ID'], ID_info['user2_ID']))
            dialogue_ID = cursor.fetchall()
            cursor.execute('select user_ID, time, message from message_history where dialogue_ID = %s and (user_ID = %s or user_ID = %s) order by time asc;' % (dialogue_ID[0][0], ID_info['user1_ID'], ID_info['user2_ID']))
            messageList = cursor.fetchall()
            # 转化成字典数组
            keys = ['user_ID', 'time', 'message']
            '''
            这里也是
            '''
            messagelist = toDictList(keys, messageList)
            return HttpResponse(json.dumps(messagelist, default=str), content_type='application/json')
        except:
            return HttpResponse(400, content_type='application/json')
