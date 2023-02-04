import sys
# sys.path.append('/data/bwj/project/model-serve/novelty')
# sys.path.append('/data/bwj/project/model-serve/models')
from novelty.compare import novelty_compare

def test_novelty_compare():
    sovereign_content_1 = '一种炸药，其特征在于，所述炸药包括如下重量百分比的组分：'
    sovereign_content_2 = '一种陶化剂，其特征在于，该陶化剂由下列重量比例成份组成。'
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
