"""
target: fk_university_id
        fk_province_id
        branch
        batch
        detail

origin:
    major_score
        schoolId : fk_university_id
        provinceId : fk_province_id
        type : branch
        batch : batch
        detail :
            year
            controlScore
            lowScore
            enrollmentType
"""
import json
import pandas as pd
from tqdm import tqdm

data = pd.read_json("total_score.json")
print("finish loading data")
# 获取学校id
school_ids = data.loc[:, "schoolId"].drop_duplicates().to_list()
# 按学校分类
school_filter = data.groupby(by="schoolId")

clean_data = []

for s_id in tqdm(school_ids):
    _data = school_filter.get_group(s_id)
    # 按省份分类
    province_ids = _data.loc[:, "provinceId"].drop_duplicates().to_list()

    province_filter = _data.groupby(by="provinceId")
    for p_id in province_ids:
        __data = province_filter.get_group(p_id)
        # 按批次分
        branch = __data.loc[:, "type"].drop_duplicates().to_list()
        branch_filter = __data.groupby(by="type")
        for b in branch:
            ___data = branch_filter.get_group(b)
            batch = ___data.loc[:, "batch"].drop_duplicates().to_list()
            batch_filter = ___data.groupby(by="batch")
            for _batch in batch:
                ____data = batch_filter.get_group(_batch)
                year = ____data.loc[:, "year"].drop_duplicates().to_list()
                year_filter = ____data.groupby(by="year")

                detail = {}
                for y in year:
                    final_data = year_filter.get_group(y)
                    detail[y] = list(
                        final_data.loc[
                            :, ["controlScore", "lowScore", "enrollmentType"]
                        ]
                        .T.to_dict()
                        .values()
                    )
                clean_data.append(
                    {
                        "fk_university_id": s_id,
                        "fk_province_id": p_id,
                        "branch": b,
                        "batch": batch,
                        "detail": detail,
                    }
                )

print("writing data")
clean_data = json.dumps(clean_data)
with open("total_score_clean.json", "w", encoding="utf8") as w:
    w.write(clean_data)
