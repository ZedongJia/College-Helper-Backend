from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.db import connection, Error

# Create your views here.
@require_http_methods(['GET'])
def match(request):
    ID = request.GET.get('ID', None)
    image = None
    useDefault = False
    with connection.cursor() as cursor:
        try:
            cursor.execute('select image from gallery where ID=%s', (ID,))
            ret = cursor.fetchall()
            if len(ret) == 0:
                useDefault = True
            else:
                image = ret[0][0]
        except Error as e:
            useDefault = True
    # test
    if useDefault:
        with open('static/test.png', 'rb') as r:
            image = r.read()
    return HttpResponse(image, content_type='image/png')