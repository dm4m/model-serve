import pymysql

def get_sig_text_by_id(id_list):
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
            cursor.execute("SELECT  `signory_seg` FROM `signory_seg` WHERE `signory_id` in (%s)" % format_strings, tuple(id_list))
            results = cursor.fetchall()
    return  results