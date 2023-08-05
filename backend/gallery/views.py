from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.db import connection, Error
from AK_Graph_Backend.settings import BASE_URL


# Create your views here.
@require_http_methods(["GET"])
def match(request):
    ID = request.GET.get("ID", None)
    image = None
    useDefault = False
    with connection.cursor() as cursor:
        try:
            cursor.execute("select image from gallery where user_ID=%s", (ID,))
            ret = cursor.fetchone()
            if ret is None:
                useDefault = True
            else:
                image = ret[0]
        except Error:
            useDefault = True
    # test
    if useDefault:
        with open("static/test.png", "rb") as r:
            image = r.read()
    return HttpResponse(image, content_type="image/png")


def store_img(user_ID, b_img):
    with connection.cursor() as cursor:
        # 查找是否存在照片
        cursor.execute("select * from gallery where user_ID=%s", (user_ID,))
        user_img = cursor.fetchone()
        if user_img is not None:
            cursor.execute("update gallery set %b where user_ID=%s", (b_img, user_ID))
        else:
            # 没有就进行插入
            cursor.execute("insert into gallery values(%s, %b)", (user_ID, b_img))
    return BASE_URL + "/gallery/match/?ID=" + str(user_ID)
