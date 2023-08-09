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
                "select id, time, type, content from browsing_history where isHistory = 'true' and user_id = %s order by time desc;",
                (ID,),
            )
            browseInfo = {}
            g_time_str = datetime(1600, 1, 1, 1, 1, 1).date().strftime("%Y年%m月%d日")
            browseHistory = cursor.fetchall()
            for row in browseHistory:
                browse_id, b_time, type, content = row
                time_str = b_time.date().strftime("%Y年%m月%d日")
                if time_str != g_time_str:
                    g_time_str = time_str
                    browseInfo[g_time_str] = []
                b_time = b_time.time()
                browseInfo[str(g_time_str)].append(
                    {
                        "time": b_time,
                        "type": type,
                        "content": content,
                        "browse_id": browse_id,
                    }
                )
            return JsonResponse({"status": True, "browseInfo": browseInfo})
    # 删除历史记录
    if request.method == "POST":
        ID = request.session.get("id", None)
        if ID is None:
            return JsonResponse({"status": False, "error": "信息错误请重新登录"})
        browse_id = request.POST.get("browse_id")

        with connection.cursor() as cursor:
            cursor.execute(
                "update browsing_history set isHistory = 'false' where id=%s",
                (browse_id,),
            )
            removeUnusedHistory()
            return JsonResponse({"status": True})

@require_http_methods(["POST"])
def star(request):
    id = request.session.get("id", None)
    if id is None:
        return JsonResponse({"status": False, "error": "信息错误请重新登录"})
    browse_id = request.POST.get("browse_id")
    state = request.POST.get("state")
    # todo
    with connection.cursor() as cursor:
        cursor.execute(
            "update browsing_history set isCollected=%s where id=%s", (state, browse_id)
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
                "select id, time, type, content from browsing_history where isCollected = 'true' and user_id = %s order by time desc;",
                (ID,),
            )
            collectionHistory = cursor.fetchall()
            collectionInfo = {}
            curr_type = ""
            for row in collectionHistory:
                collection_id, c_time, type, content = row
                if type != curr_type:
                    curr_type = type
                    collectionInfo[curr_type] = []
                collectionInfo[curr_type].append(
                    {
                        "time": c_time.strftime("%Y年%m月%d日 %H:%M:%S"),
                        "type": type,
                        "content": content,
                        "collection_id": collection_id
                    }
                )
            return JsonResponse({"status": True, "collectionInfo": collectionInfo})
    # 删除收藏记录
    if request.method == "POST":
        id = request.session.get("id", None)
        if id is None:
            return JsonResponse({"status": False, "error": "信息错误请重新登录"})
        collection_id = request.POST.get("collection_id")

        with connection.cursor() as cursor:
            cursor.execute(
                "update browsing_history set isCollected = 'false' where id=%s",
                (collection_id,),
            )
            removeUnusedHistory()
            return JsonResponse({"status": True})

def removeUnusedHistory():
    with connection.cursor() as cursor:
        cursor.execute(
            "delete from browsing_history where isHistory = 'false' and isCollected='false'",
        )

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
            "delete from session where id=%s", (session_id,)
        )
        return JsonResponse({"status": True})


@require_http_methods(["POST"])
def addBrowseInfo(request):
    # user_id
    ID = request.session.get("id", None)
    if ID is None:
        return JsonResponse({"status": False, "error": "信息错误请重新登录"})
    # time  当前时间
    time = datetime.now()
    # 类型
    type = request.POST.get("type", None)
    # 内容
    content = request.POST.get("content", None)
    with connection.cursor() as cursor:
        cursor.execute(
            "insert into browsing_history values(null, %s, %s, %s, %s, 'false', 'true')",
            (str(ID), time, type, content),
        )
        cursor.execute(
            "select id from browsing_history where user_id=%s order by time desc",
            (str(ID),),
        )
        browse_id = cursor.fetchone()[0]

    return JsonResponse({"status": True, "browse_id": browse_id})


@require_http_methods(["GET"])
def queryFollow(request):
    id = request.session.get("id", None)
    query_id = request.GET.get("query_id")
    if id is None:
        return JsonResponse({"status": False, "error": "信息错误请重新登录"})
    with connection.cursor() as cursor:
        cursor.execute("select follow_id from follow where user_id=%s", (id,))
        follow_id_list = cursor.fetchall()
        follow_id_list = [str(id[0]) for id in follow_id_list]
    if str(query_id) in follow_id_list:
        return JsonResponse({"status": True, "msg": "exist"})
    else:
        return JsonResponse({"status": True, "msg": "not exist"})


@require_http_methods(["GET"])
def queryFollowList(request):
    id = request.session.get("id", None)
    if id is None:
        return JsonResponse({"status": False, "error": "信息错误请重新登录"})
    with connection.cursor() as cursor:
        cursor.execute("select follow_id from follow where user_id=%s", (id,))
        follow_id_list = cursor.fetchall()
        followList = []
        for f in follow_id_list:
            f = f[0]
            cursor.execute("select nickname, image from user where id=%s", (f,))
            nickname, image = cursor.fetchone()
            follow = {
                'id': f,
                'nickname': nickname,
                'image': image
            }
            followList.append(follow)
        return JsonResponse({"status": True, "followList": followList})


@require_http_methods(["GET"])
def querySession(request):
    id = request.session.get("id", None)
    query_id = request.GET.get("query_id")
    if id is None:
        return JsonResponse({"status": False, "error": "信息错误请重新登录"})
    with connection.cursor() as cursor:
        cursor.execute(
            "select T.id from session as S, session as T where S.id=T.id and S.user_id=%s",
            (id,),
        )
        session_id_list = cursor.fetchall()
        session_id_list = [str(id[0]) for id in session_id_list]

    if str(query_id) in session_id_list:
        return JsonResponse({"status": True, "msg": "exist"})
    else:
        return JsonResponse({"status": True, "msg": "not exist"})


@require_http_methods(["POST"])
def follow(request):
    # add follow and session
    id = request.session.get("id", None)
    if id is None:
        return JsonResponse({"status": False, "error": "信息错误请重新登录"})
    follow_id = request.POST.get("follow_id")
    with connection.cursor() as cursor:
        cursor.execute(
            "select follow_id from follow where user_id=%s and follow_id=%s",
            (id, follow_id),
        )
        if cursor.fetchone() is not None:
            return JsonResponse({"status": False, "error": "请勿重复关注同一个人"})
        cursor.execute("insert into follow values(%s, %s)", (id, follow_id))
        cursor.execute(
            "select * from session as S, session as T where S.id=T.id and S.user_id=%s and T.user_id=%s",
            (id, follow_id),
        )
        if cursor.fetchone() is None:
            cursor.execute("select id from session order by id desc")
            cnt = cursor.fetchone()
            if cnt is None:
                cursor.execute("insert into session values(1, %s)", (id))
                cursor.execute("insert into session values(1, %s)", (follow_id))
            else:
                cursor.execute("insert into session values(%s, %s)", (cnt[0], id))
                cursor.execute(
                    "insert into session values(%s, %s)", (cnt[0], follow_id)
                )

    return JsonResponse({"status": True})


@require_http_methods(["POST"])
def addSession(request):
    # if already exists, ignore
    id = request.session.get("id", None)
    if id is None:
        return JsonResponse({"status": False, "error": "信息错误请重新登录"})
    follow_id = request.POST.get("follow_id")
    with connection.cursor() as cursor:
        cursor.execute(
            "select * from session as S, session as T where S.id=T.id and S.user_id=%s and T.user_id=%s",
            (id, follow_id),
        )
        if cursor.fetchone() is None:
            cursor.execute("select id from session order by id desc")
            cnt = cursor.fetchone()
            if cnt is None:
                cursor.execute("insert into session values(1, %s)", (id))
                cursor.execute("insert into session values(1, %s)", (follow_id))
            else:
                cursor.execute("insert into session values(%s, %s)", (cnt[0] + 1, id))
                cursor.execute(
                    "insert into session values(%s, %s)", (cnt[0] + 1, follow_id)
                )
            return JsonResponse({"status": True})
        else:
            return JsonResponse({"status": False, "error": "该会话已存在"})


@require_http_methods(["GET"])
def queryFeedback(request):
    id = request.session.get("id", None)
    if id is None:
        return JsonResponse({"status": False, "error": "信息错误请重新登录"})
    with connection.cursor() as cursor:
        cursor.execute(
            "select id, type, time, state, question, advice from feedback where user_id=%s",
            (id,),
        )
        ret = cursor.fetchall()
        feedbackDict = {}
        _typeDict = {"entity": "实体", "relation": "关系", "addNew": "新增"}
        for f in ret:
            _type = _typeDict[f[1]]
            if feedbackDict.get(_type, None) is None:
                feedbackDict[_type] = []
            feedbackDict[_type].append(
                {
                    "time": str(f[2]).replace("T", " "),
                    "id": f[0],
                    "state": f[3],
                    "question": f[4],
                    "advice": f[5],
                }
            )
        return JsonResponse({"status": True, "feedbackDict": feedbackDict})


@require_http_methods(["POST"])
def addFeedback(request):
    id = request.session.get("id", None)
    if id is None:
        return JsonResponse({"status": False, "error": "信息错误请重新登录"})
    _type = request.POST.get("type")
    question = request.POST.get("question")
    advice = request.POST.get("advice")
    image = request.FILES.get("imgSrc", None)
    if image is None:
        image = b""
    else:
        image = image.read()
    with connection.cursor() as cursor:
        cursor.execute(
            "insert into feedback values(null, %s, %s, %s, %s, %s, %b, '待处理')",
            (id, datetime.now(), _type, question, advice, image),
        )
        return JsonResponse({"status": True})


"""
                    time: '2017 5:04 01:01:01',
                    id: 1,
                    nickname: 'zhngsan',
                    image: '',
                    content: 'hhhh'
"""


@require_http_methods(["GET"])
def getReview(request):
    name = request.GET.get("name")
    label = request.GET.get("label")
    with connection.cursor() as cursor:
        cursor.execute(
            "select id, user_id, time, content from review where name=%s and label=%s order by time desc",
            (name, label),
        )
        ret = cursor.fetchall()
        reviewList = []
        for r in ret:
            review_id, user_id, time, content = r
            cursor.execute("select nickname, image from user where id=%s", (user_id,))
            nickname, image = cursor.fetchone()
            reviewList.append(
                {
                    "review_id": review_id,
                    "time": time,
                    "id": user_id,
                    "nickname": nickname,
                    "image": image,
                    "content": content,
                }
            )
        return JsonResponse({"status": True, "reviewList": reviewList})


@require_http_methods(["POST"])
def addReview(request):
    id = request.session.get("id", None)
    if id is None:
        return JsonResponse({"status": False, "error": "信息错误请重新登录"})
    name = request.POST.get("name")
    label = request.POST.get("label")
    content = request.POST.get("content")
    with connection.cursor() as cursor:
        cursor.execute(
            "insert into review values(null, %s, %s, %s, %s, %s)",
            (id, name, label, datetime.now(), content),
        )

    return JsonResponse({"status": True})


@require_http_methods(["POST"])
def removeReview(request):
    id = request.session.get("id", None)
    if id is None:
        return JsonResponse({"status": False, "error": "信息错误请重新登录"})
    review_id = request.POST.get("review_id")
    with connection.cursor() as cursor:
        cursor.execute(
            "delete from review where id=%s",
            (review_id,),
        )

    return JsonResponse({"status": True})
