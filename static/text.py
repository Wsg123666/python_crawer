# def run(username):
#     print()
#     # print(password)
#
#
# content_list = ["wsg","1234"]
# m = [content_list[m*2]+":"+content_list[m*2+1] for m in range(int(len(content_list)/2))]
# # print(m)
# q,n= m[0].split(":")
# # m = i for i in content_list
# # run(i for i in content_list)

url = dict()
url["haha"] = "jaja"
url["sadsa"] ="wwew"
print(url)
if len(url) >= 2:
    key_list = []
    for dic in url:
        key_list.append(dic)

    for list in key_list:
        url.pop(list)

print(url)