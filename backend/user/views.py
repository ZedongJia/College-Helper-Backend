import random
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.db import connection
from gallery.views import store_img
from utls.encrypt import encrypt
from utls.valid import Identity
from datetime import datetime
from AK_Graph_Backend.settings import BASE_URL

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
                    "select id, nickname, image from user where phone=%s and password=%s",
                    (account, password),
                )
            else:
                cursor.execute(
                    "select id, nickname, image from user where email=%s and password=%s",
                    (account, password),
                )
            userInfo = cursor.fetchone()

        keys = ["id", "nickname", "image"]
        if userInfo is None:
            # 查无此人
            return JsonResponse({"status": False, "error": "账号或密码错误"})

        userInfo = {keys[i]: meta for i, meta in enumerate(userInfo)}

        # 设置cookie 和 session
        response = JsonResponse({"status": True, "userInfo": userInfo})
        identity = Identity(
            str(userInfo["id"]), userInfo["nickname"], request, response
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
        image = BASE_URL + "/gallery/match?ID=-1"

        if not Identity.valid_code(request, code):
            return JsonResponse({"status": False, "error": "验证码错误"})

        password = encrypt(password)
        # 查找该人是否已存在, 利用phone, email
        with connection.cursor() as cursor:
            cursor.execute(
                "select id from user where phone=%s or email=%s", (phone, email)
            )
            if not cursor.fetchone() is None:
                return JsonResponse({"status": False, "error": "该用户已注册，请更改手机号或邮箱"})
        # 插入
        with connection.cursor() as cursor:
            cursor.execute(
                "insert into user "
                "(id, nickname, password, image, phone, gender, email, QQ, weChat)"
                'values (null, %s, %s, %s, %s, "unknown", %s, null, null)',
                (nickname, password, image, phone, email),
            )
        return JsonResponse({"status": True, "info": "注册成功"})


@require_http_methods(["GET"])
def quick(request):
    phone = request.GET.get("phone", None)
    code = request.GET.get("code", None)
    with connection.cursor() as cursor:
        cursor.execute("select id, nickname, image from user where phone=%s", (phone,))
        userInfo = cursor.fetchone()
    if userInfo is None:
        return JsonResponse({"status": False, "error": "手机号错误"})
    if not Identity.valid_code(request, code):
        return JsonResponse({"status": False, "error": "验证码错误"})
    keys = ["id", "nickname", "image"]

    userInfo = {keys[i]: meta for i, meta in enumerate(userInfo)}

    response = JsonResponse({"status": True, "userInfo": userInfo})
    identity = Identity(str(userInfo["id"]), userInfo["nickname"], request, response)
    identity.sign()
    return response


@require_http_methods(["POST"])
def updatePW(request):
    ID = request.session.get("id", None)
    if ID is None:
        return JsonResponse({"status": False, "error": "信息错误请重新登录"})
    password = request.POST.get("password")
    password = encrypt(password)
    with connection.cursor() as cursor:
        cursor.execute("update user set password=%s where id=%s", (password, ID))

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


# 根据用户ID 获取、修改用户信息
@require_http_methods(["GET", "POST"])
def userInfo(request):
    if request.method == "GET":
        ID = request.session.get("id", None)
        if ID is None:
            return JsonResponse({"status": False, "error": "信息错误请重新登录"})
        with connection.cursor() as cursor:
            cursor.execute(
                "select nickname, gender, phone, email, QQ, weChat from user where id = %s",
                (ID,),
            )
            userInfo = cursor.fetchone()
            if userInfo is None:
                return JsonResponse({"status": False, "error": "该用户不存在"})
            keys = ["nickname", "gender", "phone", "email", "QQ", "weChat"]
            userInfo = {keys[i]: meta for i, meta in enumerate(userInfo)}
            return JsonResponse({"status": True, "userInfo": userInfo})

    if request.method == "POST":
        ID = request.session.get("id", None)
        if ID is None:
            return JsonResponse({"status": False, "error": "信息错误请重新登录"})
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
            cursor.execute("select id, nickname, image from user where id=%s", (ID,))
            userInfo = cursor.fetchone()
            keys = ["id", "nickname", "image"]
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
        ID = request.session.get("id", None)
        if ID is None:
            return JsonResponse({"status": False, "error": "信息错误请重新登录"})
        with connection.cursor() as cursor:
            sql = "select " + ", ".join(keys) + " from privacy where user_id = %s;"
            cursor.execute(sql, (ID,))
            privacyInfo = cursor.fetchone()
            if privacyInfo is None:
                return JsonResponse({"status": False, "error": "没有信息"})
            # 转化成字典数组
            privacyInfo = {k: privacyInfo[i] for i, k in enumerate(keys)}
            return JsonResponse({"status": True, "privacyInfo": privacyInfo})

    if request.method == "POST":
        ID = request.session.get("id", None)
        if ID is None:
            return JsonResponse({"status": False, "error": "信息错误请重新登录"})
        values = [request.POST.get(k, "true") for k in keys]
        with connection.cursor() as cursor:
            sql = (
                "update privacy set " + "=%s, ".join(keys) + "=%s " + "where user_id=%s"
            )
            cursor.execute(
                sql,
                tuple(values) + (ID,),
            )
            return JsonResponse({"status": True})


# 根据不同用户ID 返回对应private为true的信息字段
@require_http_methods(["GET"])
def getOpenInfo(request):
    ID = request.GET.get("ID", None)
    keys = ["nickname", "image", "gender", "phone", "email", "QQ", "weChat"]
    priv_keys = [
        "telephone_priv",
        "gender_priv",
        "email_priv",
        "QQ_priv",
        "weChat_priv",
        "collection_priv",
    ]
    resultDict = {}
    with connection.cursor() as cursor:
        # 查到基本信息
        sql = "select " + ", ".join(keys) + " from user where id = %s;"
        cursor.execute(
            sql,
            (ID,),
        )
        userInfo = cursor.fetchone()
        if userInfo is None:
            return JsonResponse({"status": False, "error": "信息不存在"})
        # 查找收藏记录
        cursor.execute(
            "select time, type, content from browsing_history where user_id=%s and isCollected='true'",
            (ID,),
        )
        collected = cursor.fetchall()
        if len(collected) != 0:
            collectionDict = {}
            curr_type = ""
            for row in collected:
                time, type, content = row
                if type != curr_type:
                    curr_type = type
                    collectionDict[curr_type] = []
                collectionDict[curr_type].append(
                    {
                        "time": time.strftime("%Y年%m月%d日 %H:%M:%S"),
                        "type": type,
                        "content": content,
                    }
                )
        else:
            collectionDict = {}
        # 查找privacy
        sql = "select " + ", ".join(priv_keys) + " from privacy where user_id = %s;"
        cursor.execute(sql, (ID,))
        priv = cursor.fetchone()
        # 添加信息
        resultDict["nickname"] = userInfo[0]
        resultDict["image"] = userInfo[1]
        # 检验是否加入
        resultDict["gender"] = userInfo[2] if priv[1] == "true" else "未公开"
        resultDict["phone"] = userInfo[3] if priv[0] == "true" else "未公开"
        resultDict["email"] = userInfo[4] if priv[2] == "true" else "未公开"
        resultDict["QQ"] = userInfo[5] if priv[3] == "true" else "未公开"
        resultDict["weChat"] = userInfo[6] if priv[4] == "true" else "未公开"
        resultDict["collectionDict"] = collectionDict if priv[5] == "true" else "未公开"

        return JsonResponse({"status": True, "openDict": resultDict})


# 根据用户ID 获取、删除历史记录
def getBrowseInfo(request):
    # 获取历史记录
    if request.method == "GET":
        ID = request.session.get("id", None)
        if ID is None:
            return JsonResponse({"status": False, "error": "信息错误请重新登录"})
        with connection.cursor() as cursor:
            cursor.execute(
                "select time, type, content from browsing_history where isHistory = 'true' and user_id = %s order by time desc;",
                (ID,),
            )
            browseInfo = {}
            g_time_str = datetime(1600, 1, 1, 1, 1, 1).date().strftime("%Y年%m月%d日")
            browseHistory = cursor.fetchall()
            for row in browseHistory:
                b_time, type, content = row
                time_str = b_time.date().strftime("%Y年%m月%d日")
                if time_str != g_time_str:
                    g_time_str = time_str
                    browseInfo[g_time_str] = []
                b_time = b_time.time()
                browseInfo[str(g_time_str)].append(
                    {"time": b_time, "type": type, "content": content}
                )
            return JsonResponse({"status": True, "browseInfo": browseInfo})
    # 删除历史记录
    if request.method == "POST":
        ID = request.session.get("id", None)
        if ID is None:
            return JsonResponse({"status": False, "error": "信息错误请重新登录"})
        b_time = request.POST.get("time")
        type = request.POST.get("type")
        content = request.POST.get("content")

        with connection.cursor() as cursor:
            cursor.execute(
                "update browsing_history set isHistory = 'false' where user_id=%s and time = %s and type = %s and content = %s;",
                (ID, datetime.strptime(b_time, "%Y年%m月%d日%H:%M:%S"), type, content),
            )
            return JsonResponse({"status": True})


# 根据用户ID 获取、删除收藏记录
def getCollectionInfo(request):
    # 获取收藏记录
    if request.method == "GET":
        ID = request.session.get("id", None)
        if ID is None:
            return JsonResponse({"status": False, "error": "信息错误请重新登录"})
        with connection.cursor() as cursor:
            cursor.execute(
                "select time, type, content from browsing_history where isCollected = 'true' and user_id = %s order by time desc;",
                (ID,),
            )
            collectionHistory = cursor.fetchall()
            collectionInfo = {}
            curr_type = ""
            for row in collectionHistory:
                c_time, type, content = row
                if type != curr_type:
                    curr_type = type
                    collectionInfo[curr_type] = []
                collectionInfo[curr_type].append(
                    {
                        "time": c_time.strftime("%Y年%m月%d日 %H:%M:%S"),
                        "type": type,
                        "content": content,
                    }
                )
            return JsonResponse({"status": True, "collectionInfo": collectionInfo})
    # 删除收藏记录
    if request.method == "POST":
        id = request.session.get("id", None)
        if id is None:
            return JsonResponse({"status": False, "error": "信息错误请重新登录"})
        c_time = request.POST.get("time")
        type = request.POST.get("type")
        content = request.POST.get("content")

        with connection.cursor() as cursor:
            cursor.execute(
                "update browsing_history set isCollected = 'false' where user_id=%s and time = %s and type = %s and content = %s;",
                (ID, datetime.strptime(c_time, "%Y年%m月%d日 %H:%M:%S"), type, content),
            )
            return JsonResponse({"status": True})


# 根据id获取聊天session和对象
@require_http_methods(["GET"])
def getSession(request):
    ID = request.session.get("id", None)
    if ID is None:
        return JsonResponse({"status": False, "error": "信息错误请重新登录"})

    with connection.cursor() as cursor:
        # 查询该id下的所有对话
        cursor.execute("select id from session where user_id=%s", (ID,))
        session_id_list = cursor.fetchall()
        # 查询该id下的所有follow对象
        cursor.execute("select follow_id from follow where user_id=%s", (ID,))
        follow_id_list = [id[0] for id in cursor.fetchall()]
        sessionInfo = {"临时会话": [], "好友": []}
        # 查询会话下的所有信息
        for session_id in session_id_list:
            session_id = session_id[0]
            # 默认是二人对话
            cursor.execute(
                "select user_id from session where id=%s and user_id<>%s",
                (session_id, ID),
            )
            id = cursor.fetchone()
            if id is None:
                continue
            id = id[0]
            # 获取该用户该session的最后一条记录的时间
            cursor.execute(
                "select time from message where session_id=%s order by time desc",
                (session_id,),
            )
            s_time = cursor.fetchone()
            if s_time is None:
                s_time = "--:--:--"
            else:
                s_time = s_time[0].strftime("%H:%M:%S")
            # 查询用户信息
            cursor.execute("select nickname, image from user where id=%s", (id,))
            info = cursor.fetchone()
            info = {"id": id, "img": info[1], "content": info[0]}
            if id in follow_id_list:
                sessionInfo["好友"].append(
                    {"time": s_time, "info": info, "session_id": session_id}
                )
            else:
                sessionInfo["临时会话"].append(
                    {"time": s_time, "info": info, "session_id": session_id}
                )

        return JsonResponse({"status": True, "sessionInfo": sessionInfo})


# 根据session获取聊天记录
@require_http_methods(["GET"])
def getMessageList(request):
    m_time = request.GET.get("time")
    endTime = m_time
    session_id = request.GET.get("session_id")
    if session_id is None:
        return JsonResponse({"status": False, "error": "会话不存在"})

    with connection.cursor() as cursor:
        if m_time == "--":
            cursor.execute(
                "select user_id, time, content from message where session_id=%s",
                (session_id),
            )
        else:
            cursor.execute(
                "select user_id, time, content from message where session_id=%s and time > %s",
                (session_id, m_time),
            )
        messageResult = cursor.fetchall()
        messageList = []
        for i, message in enumerate(messageResult):
            messageList.append(
                {"ID": message[0], "time": message[1], "content": message[2]}
            )
            if i == 0:
                endTime = message[1]
            elif message[1] > endTime:
                endTime = message[1]
    return JsonResponse(
        {"status": True, "data": {"endTime": endTime, "messageList": messageList}}
    )


@require_http_methods(["POST"])
def addMessage(request):
    session_id = request.POST.get("session_id")
    id = request.session.get("id", None)
    if id is None:
        return JsonResponse({"status": False, "error": "信息错误请重新登录"})
    m_time = request.POST.get("time")
    print(m_time)
    m_time = datetime.fromtimestamp(int(m_time) / 1000)
    content = request.POST.get("content")
    with connection.cursor() as cursor:
        cursor.execute(
            "insert into message values(%s, %s, %s, %s)",
            (session_id, id, m_time, content),
        )
        return JsonResponse({"status": True})


r"""
日期：入：timestamp
     出：datetime

"""


@require_http_methods(["POST"])
def dropSession(request):
    id = request.session.get("id", None)
    if id is None:
        return JsonResponse({"status": False, "error": "信息错误请重新登录"})
    session_id = request.POST.get("session_id")
    with connection.cursor() as cursor:
        cursor.execute(
            "delete from session where user_id=%s and id=%s", (id, session_id)
        )
        return JsonResponse({"status": True})


# @require_http_methods(["GET"])
# def follow(request):
#     id = request.