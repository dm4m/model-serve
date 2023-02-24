import pymysql

def get_sig_by_id(id_list):
    """
    return:
    [
        {
            patent_id: ,
            title: ,
            signory_seg:
        },
        ...
    ]
    """

    mysql_connection = pymysql.connect(host='10.108.119.71',
                                      user='bwj',
                                      password='bwj',
                                      database='patent',
                                      cursorclass=pymysql.cursors.DictCursor)
    results = []
    with mysql_connection:
        with mysql_connection.cursor() as cursor:
            # Read a single record
            format_strings = ','.join(['%s'] * len(id_list))
            cursor.execute("SELECT  `patent_id`, `title`, `signory_seg`, `signory_id`  FROM `signory_seg`, `patent` WHERE `signory_id` in (%s) and `signory_seg`.`patent_id` = `patent`.`id`" % format_strings, tuple(id_list))
            results = cursor.fetchall()
    return  results

def get_class_by_id(id):
    # 用于通过id，获取class，以评价检索效果
    mysql_connection = pymysql.connect(host='10.108.119.71',
                                      user='bwj',
                                      password='bwj',
                                      database='patent',
                                      cursorclass=pymysql.cursors.DictCursor)
    results = []
    with mysql_connection:
        with mysql_connection.cursor() as cursor:
            # Read a single record
            cursor.execute("SELECT  `display_mainclass_code`,`display_class_list`  FROM `patent` WHERE `id`= " +str(id))
            results = cursor.fetchall()
    res = []
    # print(results)
    res.append(results[0]['display_mainclass_code'])
    res.append(results[0]['display_class_list'].split(";"))
    return  res