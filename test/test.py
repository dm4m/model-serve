import sys
# sys.path.append('/data/bwj/project/model-serve/novelty')
# sys.path.append('/data/bwj/project/model-serve/models')
from novelty.compare import novelty_compare
from repository.mysql_source import get_sig_by_id
from services.novelty_service import signory_item_analysis
import pymysql

def test_get_sig_by_id():
    id_list = [1, 2]
    result = get_sig_by_id(id_list)
    print(result)

def test_signory_item_analysis():
    item = "一种铜基形状记忆合金，包含20％(重量) 锌和5％(重量) 铝。"
    signory_item_analysis(item)

def test_novelty_compare():
    sovereign_content_1 = '5.一种铜基形状记忆合金，包含20％(重量) 锌和5％(重量) 铝。'
    sovereign_content_2 = '5.一种铜基形状记忆合金，包含10％～35％(重量) 的锌和2％～8％(重量) 的铝，余量为铜。'
    print(novelty_compare(sovereign_content_2, sovereign_content_1))

def test_mysql():
    mysql_connection = pymysql.connect(host='152.136.114.189',
                                    port=6336,
                                      user='bwj',
                                      password='bwj',
                                      database='patent',
                                      cursorclass=pymysql.cursors.DictCursor)

if __name__ == '__main__':
    # load_model()
    # test_get_sig_by_id()
    #  models.init_app()
    # test_signory_item_analysis()
    test_novelty_compare()
    # test_mysql()