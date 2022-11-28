from repository.mysql_source import get_sig_text_by_id
from services.analysis_service import signory_item_analysis

def test_get_sig_text_by_id():
    id_list = [1, 2]
    result = get_sig_text_by_id(id_list)
    print(result)

def test_signory_item_analysis():
    item = "烟花"
    signory_item_analysis(item)

if __name__ == '__main__':
    # load_model()
   # test_get_sig_text_by_id()
   #  models.init_app()
    test_signory_item_analysis