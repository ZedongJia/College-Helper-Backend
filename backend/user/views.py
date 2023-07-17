import random
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.db import connection, Error
from user.user import User

# from neo4j_model.db_pool import DB_POOL

# Create your views here.


@require_http_methods(["GET"])
def login(request):
    account = request.GET.get('account', None)
    password = request.GET.get('password', None)
    password = User.encode(password)

    if account == None or password == None:
        return HttpResponse(400, content_type='application/json')

    with connection.cursor() as cursor:
        try:
            cursor.execute('select * from user where account=%s and password=%s', (account, password))
            userInfo = cursor.fetchall()
            # 获取userInfo的Json
            user = User(userInfo)
            # 设置cookier
            response = HttpResponse(str(user), content_type='application/json')
            response.set_signed_cookie(**user.getCookie(), salt='?zrgj2023?', max_age=60 * 60)
            return response
        except Error as e:
            return HttpResponse(400, content_type='application/json')

@require_http_methods(["POST"])
def register(request):
    account = request.POST.get('account', None)
    password = request.POST.get('password', None)
    # print(request.POST)
    # params = json.loads(request.body)
    # account = params['account']
    # password = params['password']
    password = User.encode(password)

    if account == None or password == None:
        return HttpResponse(400, content_type='application/json')
    
    with connection.cursor() as cursor:
        try:
            cursor.execute('insert into user values(null, %s, %s, %s, null, null, "unknown", null, null, null)', (account, account, password))
        except Error as e:
            return HttpResponse(400, content_type='application/json')
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
        return HttpResponse(200, content_type='application/json')

@require_http_methods(['GET'])
def logout(request):
    uuid = request.get_signed_cookie("uuid", default=None, salt="?zrgj2023?", max_age=None)
    if uuid == None:
        return HttpResponse(200, content_type='application/json')
    response = HttpResponse(200, content_type='application/json')
    response.delete_cookie(uuid)
    return response

@require_http_methods(['GET'])
def valid(request):
    uuid = request.get_signed_cookie("uuid", default=None, salt="?zrgj2023?", max_age=None)
    if uuid == None:
        return HttpResponse(400, content_type='application/json')
    else:
        return HttpResponse(200, content_type='application/json')

@require_http_methods(['GET'])
def verify(request):
    length = 6
    verification = []
    for _ in range(length):
        verification.append(str(random.randint(0,9)))
    return HttpResponse(''.join(verification), content_type='application/json')