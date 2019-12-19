# replace into 跟 insert 功能类似，不同点在于：
# replace into 首先尝试插入数据到表中，
# 1. 如果发现表中已经有此行数据（根据主键或者唯一索引判断）则先删除此行数据，然后插入新的数据。
# 2. 否则，直接插入新数据。


def insert_from_dic(Database_obj, table_name, dic):
    ls = [(k, dic[k]) for k in dic if dic[k] is not None]
    sql = 'replace %s (' % table_name + ','.join([i[0] for i in ls]) + \
          ') values (' + ','.join(['%r' % i[1] for i in ls]) + ');'
    rs = Database_obj.execute(sql)
    # Database_obj.commit()
    if rs > 0:
        return True
    else:
        return False


def insert_many_from_dic(Database_obj, table_name, dic_list):
    ls = [(k, dic_list[0][k]) for k in dic_list[0] if dic_list[0][k] is not None]
    sql = 'replace %s (' % table_name + ','.join([i[0] for i in ls]) + \
          ') values (' + ','.join(['%s' for i in ls]) + ');'
    tuple_list = []
    for dic in dic_list:  # dic_list to tuple_list
        item_list = [(dic[k]) for k in dic if dic[k] is not None]
        tuple_list.append(tuple(item_list))
    rs = Database_obj.get_cursor().executemany(sql, tuple_list)
    # Database_obj.commit()
    if rs > 0:
        return True
    else:
        return False
