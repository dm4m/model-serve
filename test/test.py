import sys
# sys.path.append('/data/bwj/project/model-serve/novelty')
# sys.path.append('/data/bwj/project/model-serve/models')
from novelty.compare import novelty_compare

def test_novelty_compare():
    sovereign_content_1 = '一种铜基形状记忆合金，包含20％(重量) 锌和5％(重量) 铝。'
    sovereign_content_2 = '一种铜基形状记忆合金，包含10％～35％(重量) 的锌和2％～8％(重量) 的铝，余量为铜。'
    # sovereign_content_1 = '该装置由螺钉构成。'
    # sovereign_content_2 = '螺栓构成了该装置。'
    print(novelty_compare(sovereign_content_2, sovereign_content_1))

if __name__ == '__main__':
    # load_model()
    # test_get_sig_by_id()
    #  models.init_app()
    # test_signory_item_analysis()
    test_novelty_compare()
    # test_mysql()