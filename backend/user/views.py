import random
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.db import connection
from gallery.views import store_img
from utls.encrypt import encrypt
from utls.valid import Identity

# from neo4j_model.db_pool import DB_POOL
# Create your views here.


@require_http_methods(["GET", "POST"])
def account(request):
    r"""
    登录接口, 注册接口
    """
    if request.method == "GET":
        # 获取基本信息
        account = request.GET.get("account", None)
        password = request.GET.get("password", None)
        use = request.GET.get("use", "phone")
        password = encrypt(password)
        # 查询
        with connection.cursor() as cursor:
            if use == "phone":
                cursor.execute(
                    "select ID, nickname, image from user where phone=%s and password=%s",
                    (account, password),
                )
            else:
                cursor.execute(
                    "select ID, nickname, image from user where email=%s and password=%s",
                    (account, password),
                )
            userInfo = cursor.fetchone()

        keys = ["ID", "nickname", "image"]
        if userInfo is None:
            # 查无此人
            return JsonResponse({"status": False, "error": "账号或密码错误"})

        userInfo = {keys[i]: meta for i, meta in enumerate(userInfo)}

        # 设置cookie 和 session
        response = JsonResponse({"status": True, "userInfo": userInfo})
        identity = Identity(
            str(userInfo["ID"]), userInfo["nickname"], request, response
        )
        identity.sign()
        return response
    else:
        # 获取基本信息
        nickname = request.POST.get("nickname", None)
        email = request.POST.get("email", None)
        phone = request.POST.get("phone", None)
        password = request.POST.get("password", None)
        code = request.POST.get("code", None)

        if not Identity.valid_code(request, code):
            return JsonResponse({"status": False, "error": "验证码错误"})

        password = encrypt(password)
        # 查找该人是否已存在, 利用phone
        with connection.cursor() as cursor:
            cursor.execute("select ID from user where phone=%s", (phone,))
            if not cursor.fetchone() is None:
                return JsonResponse({"status": False, "error": "该手机号已注册"})
        # 插入
        with connection.cursor() as cursor:
            cursor.execute(
                "insert into user "
                "(ID, nickname, password, image, phone, gender, email, QQ, weChat)"
                'values (null, %s, %s, null, %s, "unknown", %s, null, null)',
                (nickname, password, phone, email),
            )
        return JsonResponse({"status": True, "info": "注册成功"})


@require_http_methods(["GET"])
def quick(request):
    phone = request.GET.get("phone", None)
    code = request.GET.get("code", None)
    with connection.cursor() as cursor:
        cursor.execute("select ID, nickname, image from user where phone=%s", (phone,))
        userInfo = cursor.fetchone()
    if userInfo is None:
        return JsonResponse({"status": False, "error": "手机号错误"})
    if not Identity.valid_code(request, code):
        return JsonResponse({"status": False, "error": "验证码错误"})
    keys = ["ID", "nickname", "image"]

    userInfo = {keys[i]: meta for i, meta in enumerate(userInfo)}

    response = JsonResponse({"status": True, "userInfo": userInfo})
    identity = Identity(str(userInfo["ID"]), userInfo["nickname"], request, response)
    identity.sign()
    return response


@require_http_methods(["POST"])
def updatePW(request):
    ID = request.POST.get("ID")
    password = request.POST.get("password")
    password = encrypt(password)
    with connection.cursor() as cursor:
        cursor.execute("update user set password=%s where ID=%s", (password, ID))

    return JsonResponse({"status": True, "info": "修改成功"})


@require_http_methods(["GET"])
def getcode(request):
    code = random.Random().randrange(111111, 999999)
    print("验证码是: " + str(code))
    Identity.set_code(request, code)
    return JsonResponse({"status": True, "info": "验证码发送成功"})


@require_http_methods(["GET"])
def state(request):
    # 前端发送的true不是True
    if request.GET.get("logout") == "true":
        response = HttpResponse(200, content_type="application/json")
        Identity.drop(request, response)
        return response
    else:
        # 验证是否有效
        valid = Identity.valid(request)
        if valid:
            return HttpResponse(200, content_type="application/json")
        else:
            return HttpResponse(400, content_type="application/json")


@require_http_methods(["GET"])
def verify(request):
    length = 6
    verification = []
    for _ in range(length):
        verification.append(str(random.randint(0, 9)))
    return HttpResponse("".join(verification), content_type="application/json")


# 根据用户ID 获取、修改用户信息
@require_http_methods(["GET", "POST"])
def userInfo(request):
    if request.method == "GET":
        ID = request.GET.get("ID", None)
        with connection.cursor() as cursor:
            cursor.execute(
                "select nickname, gender, phone, email, QQ, weChat from user where ID = %s",
                (ID,),
            )
            userInfo = cursor.fetchone()
            if userInfo is None:
                return JsonResponse({"status": False, "error": "该用户不存在"})
            keys = ["nickname", "gender", "phone", "email", "QQ", "weChat"]
            userInfo = {keys[i]: meta for i, meta in enumerate(userInfo)}
            return JsonResponse({"status": True, "userInfo": userInfo})

    if request.method == "POST":
        ID = request.POST.get("ID")
        keys = ["nickname", "gender", "phone", "email", "QQ", "weChat"]
        values = [
            request.POST.get("nickname", ""),
            request.POST.get("gender", ""),
            request.POST.get("phone", ""),
            request.POST.get("email", ""),
            request.POST.get("QQ", ""),
            request.POST.get("weChat", ""),
        ]
        image = request.FILES.get("imgUrl", None)
        if image is not None:
            imageUrl = store_img(ID, image.read())
            keys.append("image")
            values.append(imageUrl)
        with connection.cursor() as cursor:
            sql = "update user set " + "=%s, ".join(keys) + "=%s " + "where ID=%s"
            cursor.execute(
                sql,
                tuple(values) + (ID,),
            )
            cursor.execute("select ID, nickname, image from user where ID=%s", (ID,))
            userInfo = cursor.fetchone()
            keys = ["ID", "nickname", "image"]
            userInfo = {k: userInfo[i] for i, k in enumerate(keys)}
            return JsonResponse({"status": True, "userInfo": userInfo})


# 根据用户ID 获取、修改privacy信息
def privacyInfo(request):
    keys = [
        "telephone_priv",
        "gender_priv",
        "email_priv",
        "QQ_priv",
        "weChat_priv",
        "collection_priv",
    ]
    if request.method == "GET":
        ID = request.GET.get("ID", None)
        with connection.cursor() as cursor:
            sql = "select " + ", ".join(keys) + " from privacy where user_ID = %s;"
            cursor.execute(sql, (ID,))
            privacyInfo = cursor.fetchone()
            if privacyInfo is None:
                return JsonResponse({"status": False, "error": "没有信息"})
            # 转化成字典数组
            privacyInfo = {k: privacyInfo[i] for i, k in enumerate(keys)}
            return JsonResponse({"status": True, "privacyInfo": privacyInfo})

    if request.method == "POST":
        ID = request.POST.get("ID")
        values = [request.POST.get(k, "true") for k in keys]
        with connection.cursor() as cursor:
            sql = "update privacy set " + "=%s, ".join(keys) + "=%s " + "where user_ID=%s"
            cursor.execute(
                sql,
                tuple(values) + (ID,),
            )
            return JsonResponse({"status": True})


# # 根据用户ID 返回对应private为true的信息字段
# @require_http_methods(['GET'])
# def getTruePrivacy(request):
#     account_id = request.GET.get('id', None)
#     if account_id == None:
#         return HttpResponse(400, content_type='application/json')
#     with connection.cursor() as cursor:
#         try:
#             cursor.execute('select * from privacy where user_ID = %s;' % account_id)
#             privacyInfo = cursor.fetchall()[0]
#             cursor.execute("select column_name from information_schema.columns where table_name = 'privacy'")
#             keys = cursor.fetchall()
#             key = []
#             for i in range(len(privacyInfo)):
#                 if(privacyInfo[i] == 'true'):
#                     key.append(keys[i])
#             return HttpResponse(json.dumps(key), content_type='application/json')
#         except Error as e:
#             return HttpResponse(400, content_type='application/json')

# # 根据用户ID 获取、删除历史记录
# def BrowseInfo(request):
#     # 获取历史记录
#     if request.method == 'GET':
#         account_id = request.GET.get('id', None)
#         if account_id == None:
#             return HttpResponse(400, content_type='application/json')
#         with connection.cursor() as cursor:
#             try:
#                 cursor.execute("select time, type, content from browsing_history where isHistory = 'true' and user_ID = %s order by time desc;" % account_id)
#                 BrowseHistory = cursor.fetchall()
#                 '''
#                 这里也是
#                 '''
#                 keys = ['time', 'type', 'content']
#                 browseInfo = toDictList(keys, BrowseHistory)
#                 return HttpResponse(json.dumps(browseInfo, default=str), content_type='application/json')
#             except Error as e:
#                 return HttpResponse(400, content_type='application/json')
#     # 删除历史记录
#     if request.method == 'POST':
#         info = request.GET    #  time、type、user_ID
#         if info == None:
#             return HttpResponse(400, content_type='application/json')

#         with connection.cursor() as cursor:
#             try:
#                 cursor.execute("update browsing_history set isHistory = 'false' where time = '%s' and type = '%s' and user_ID = %s;" % (info['time'], info['type'], info['user_ID']))
#                 return HttpResponse(200, content_type='application/json')
#             except:
#                 return HttpResponse(400, content_type='application/json')


# # 根据用户ID 获取、删除收藏记录
# def CollectedInfo(request):
#     # 获取收藏记录
#     if request.method == 'GET':
#         info = request.GET    #  user_ID
#         print(info['user_ID'])
#         if info == None:
#             return HttpResponse(400, content_type='application/json')

#         with connection.cursor() as cursor:
#             try:
#                 cursor.execute("select time, type, content from browsing_history where isCollected = 'true' and user_ID = %s order by time desc;" % (info['user_ID']))
#                 CollectedInfo = cursor.fetchall()
#                 # 转化成字典数组
#                 keys = ['time', 'type', 'content']
#                 '''
#                 这里也是
#                 '''
#                 collectedInfo = toDictList(keys, CollectedInfo)
#                 return HttpResponse(json.dumps(collectedInfo, default=str), content_type='application/json')
#             except Error as e:
#                 return HttpResponse(400, content_type='application/json')
#     # 删除收藏记录
#     if request.method == 'POST':
#         info = request.GET    #  time、type、user_ID
#         if info == None:
#             return HttpResponse(400, content_type='application/json')

#         with connection.cursor() as cursor:
#             try:
#                 cursor.execute("update browsing_history set isCollected = 'false' where time = '%s' and type = '%s' and user_ID = %s;" % (info['time'], info['type'], info['user_ID']))
#                 return HttpResponse(200, content_type='application/json')
#             except:
#                 return HttpResponse(400, content_type='application/json')


# # 根据ID1和ID2获取聊天记录
# @require_http_methods(['GET'])
# def getMessageList(request):
#     ID_info = request.GET    # user1_ID  user2_ID
#     if ID_info == None:
#         return HttpResponse(400, content_type='application/json')

#     with connection.cursor() as cursor:
#         try:
#             cursor.execute('select ID from dialogue where user1_ID = %s and user2_ID = %s' % (ID_info['user1_ID'], ID_info['user2_ID']))
#             dialogue_ID = cursor.fetchall()
#             cursor.execute('select user_ID, time, message from message_history where dialogue_ID = %s and (user_ID = %s or user_ID = %s) order by time asc;' % (dialogue_ID[0][0], ID_info['user1_ID'], ID_info['user2_ID']))
#             messageList = cursor.fetchall()
#             # 转化成字典数组
#             keys = ['user_ID', 'time', 'message']
#             '''
#             这里也是
#             '''
#             messagelist = toDictList(keys, messageList)
#             return HttpResponse(json.dumps(messagelist, default=str), content_type='application/json')
#         except:
#             return HttpResponse(400, content_type='application/json')
