import json
import random
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.db import connection, Error
from user.user import User
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