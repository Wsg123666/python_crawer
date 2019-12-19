def type2sql(value):
    if type(value) == int:
        return "%d"
    elif type(value) == float:
        return "%f"
    else:
        return "%s"


def insert_from_dic(Database_obj, table_name, dic):
    ls = [(k, dic[k]) for k in dic if dic[k] is not None]
    sql = 'insert %s (' % table_name + ','.join([i[0] for i in ls]) + \
          ') values (' + ','.join(['%r' % i[1] for i in ls]) + ');'
    rs = Database_obj.execute(sql)
    # Database_obj.commit()
    if rs > 0:
        return True
    else:
        return False


def insert_many_from_dic(Database_obj, table_name, dic_list):
    ls = [(k, dic_list[0][k]) for k in dic_list[0] if dic_list[0][k] is not None]
    sql = 'insert %s (' % table_name + ','.join([i[0] for i in ls]) + \
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


# key存在则不操作，key不存在则插入
def insert_ignore_many_from_dic(Database_obj, table_name, dic_list):
    ls = [(k, dic_list[0][k]) for k in dic_list[0] if dic_list[0][k] is not None]
    sql = 'insert IGNORE INTO %s (' % table_name + ','.join([i[0] for i in ls]) + \
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