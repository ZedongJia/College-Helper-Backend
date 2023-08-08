r'''
## ! 这里只有有两个函数

```
def chatChoice
    ...
    # 用于没有识别到任何实体的情况下，只需要把用户的输入完整送入就可以
```
```
def AIResponse
    ...
    # 这种情况，识别到实体，则需要根据对应实体关系，生成关系列表
```
'''
# For prerequisites running the following sample, visit https://help.aliyun.com/document_detail/611472.html
"""
pip install dashscope

"""
from dashscope import Generation
from http import HTTPStatus

"""
天津市-有-政策
大学有什么
754 - 政策
"""
API_KEY = "sk-c1a770bbdf82424ea1e61ec68e1aae64"



def chatChoice(user_input):
    return "请求已注释，使用需打开"
    # response = Generation.call(model="qwen-v1", prompt=user_input, api_key=API_KEY, enable_search=True)
    # # The response status_code is HTTPStatus.OK indicate success,
    # # otherwise indicate request is failed, you can get error code
    # # and message from code and message.
    # if response.status_code == HTTPStatus.OK:
    #     result_text = response.output["text"]  # The output text
    #     return result_text
    # else:
    #     print(response.code)  # The error code.
    #     print(response.message)  # The error message.
    #     return "对不起，出了点小问题，请您重试"



def AIResponse(relation_list: list, identity: str = "志愿填报老师", target: str = "报志愿的学生"):
    r"""
    @param `relation_list` --关系列表
    @summary
    例如:
    ```
    relation_list = [
        "高考考了744分",
        "可以上清北大学、南清大学",
        "可以去清北大学计算机专业、南清大学计算机专业",
    ]
    ```
    @param `identity` --身份 '志愿填报老师'
    @param `target` --提问者身份 '报志愿的学生'

    """


    relation_list = [
        str(i + 1) + "." + relation + "\n" for i, relation in enumerate(relation_list)
    ]

    prefix_identity = "你现在的身份是一个" + identity

    prefix_refer = "请你根据以下信息:“\n" + "".join(relation_list) + "”"
    prefix_target = "为" + target + "生成一个富有温情的回复。"
    text = ",".join(
        [
            prefix_identity,
            prefix_refer,
            prefix_target,
        ]
    )
    return "请求已注释，使用需打开"
    # response = Generation.call(model="qwen-v1", prompt=text, api_key=API_KEY)
    # # The response status_code is HTTPStatus.OK indicate success,
    # # otherwise indicate request is failed, you can get error code
    # # and message from code and message.
    # if response.status_code == HTTPStatus.OK:
    #     result_text = response.output["text"]  # The output text
    #     return result_text
    # else:
    #     print(response.code)  # The error code.
    #     print(response.message)  # The error message.
    #     return "对不起，出了点小问题，请您重试"


if __name__ == "__main__":
    identity = "报考老师"
    target = "报志愿的学生"
    relation_list = [
        "高考考了744分",
        "可以上清北大学、南清大学",
        "可以去清北大学计算机专业、南清大学计算机专业",
    ]
    print("回复:" + AIResponse(relation_list, identity, target))
