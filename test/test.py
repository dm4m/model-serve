import sys
# sys.path.append('/data/bwj/project/model-serve/novelty')
# sys.path.append('/data/bwj/project/model-serve/models')
from novelty.compare import novelty_compare

def test_novelty_compare():
    sovereign_content_1 = '根据权利要求1-4任一项所述的炸药，其特征在于，所述纳米玄武岩粉的粒径为10-100nm。'
    sovereign_content_2 = '根据权利要求1-4任一项所述的炸药，其特征在于，所述纳米玄武岩粉的粒径为10-100nm。'
    print(novelty_compare(sovereign_content_2, sovereign_content_1))

if __name__ == '__main__':
    # load_model()
    # test_get_sig_by_id()
    #  models.init_app()
    # test_signory_item_analysis()
    test_novelty_compare()
    # test_mysql()
