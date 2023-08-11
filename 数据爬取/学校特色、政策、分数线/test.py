'''
读取province_idx.txt
把每一行都用, 分割
得到list[[idx, name],[]]

'''
province_map = {}
fp = open('province_idx.txt', 'r')
line = fp.readline()
while line:
    province_map[line.split(",")[1].replace("\n","")] = line.split(",")[0]
    line = fp.readline()
fp.close()
print(province_map)