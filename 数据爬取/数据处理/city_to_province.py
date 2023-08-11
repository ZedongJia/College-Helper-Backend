with open("./entity&rel_index/city_idx.txt", "r", encoding="utf8") as r:
    citys = r.readlines()
citys = [c.strip('\n').split(",") for c in citys]

with open("./entity&rel_index/province_idx.txt", "r", encoding="utf8") as r:
    provinces = r.readlines()
provinces = [p.strip('\n').split(",") for p in provinces]
rel_city_prov = []
loss_city = []

for c_idx, c_name in citys:
    found = False
    for p_idx, p_name in provinces:
        if c_name.startswith(p_name):
            rel_city_prov.append(",".join([c_idx, c_name, p_idx]))
            found = True
            break
    if not found:
        loss_city.append(",".join([c_idx, c_name]))

with open("loss_city.txt", "w", encoding="utf8") as w:
    w.write("\n".join(loss_city))

with open("city_porv_idx.txt", "w", encoding="utf8") as w:
    w.write("\n".join(rel_city_prov))
