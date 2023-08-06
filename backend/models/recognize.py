import jieba
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Recognize:
    mapper = None
    tokenizer = None

    @staticmethod
    def initial():
        Recognize._load_mapper()
        Recognize._load_dict()

    @staticmethod
    def _load_mapper():
        with open(
            os.path.join(BASE_DIR, "mapper.json"),
            "r",
            encoding="utf8",
        ) as r:
            Recognize.mapper = json.load(r)

    @staticmethod
    def _load_dict():
        jieba.load_userdict(os.path.join(BASE_DIR, "dict.txt"))

    @staticmethod
    def recognize(sentence: str) -> dict:
        r"""
        @return {
            pos: {
                name: str,
                label: str
            },
            ...
        }
        """
        # 利用jieba进行分词
        gen = jieba.cut(sentence)

        # 记录初始位置
        pos = 0

        # 加载实体哈希映射
        mapper = Recognize.mapper
        cut_list = [word for word in gen]
        cut_dict = {}

        for word in cut_list:
            if mapper.get(word, None) is None:
                # 非实体，放弃
                pos += len(word)
            else:
                # 记录
                cut_dict[pos] = {"name": word, "label": mapper[word]}
                pos += len(word)
        return {
            'cut_list': cut_list,
            'cut_dict': cut_dict
        }
