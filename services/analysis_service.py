import re
from novelty.compare import novelty_compare
from repository.milvus_source import get_relevant_id_list
from repository.mysql_source import get_sig_by_id


def novelty_analysis(pdf_file):
    signory_text = signory_extract(pdf_file)
    signory_items = signory_split(signory_text)
    analysis_res = signory_analysis(signory_items)
    return analysis_res

def signory_extract(pdf_file):
    signory = ""
    for page in pdf_file.pages:
        cur_text = page.extract_text().replace("　", "").replace(" ", "")
        if "权利要求书" in cur_text and "说明书" not in cur_text:
            signory += cur_text
    return signory

def signory_split(signory):
    signory_list = []
    if (signory is not None and len(signory) > 0):
        # 去空格
        signory = signory.replace(" ", "").replace("\n", "")
        # 去
        signory = re.sub("<imgfile=.*\/>", "", signory)
        # 去“权利要求书”
        begin_index = signory.find("页1")
        signory = signory[begin_index + 1 : ]
        if (signory[0:5] == "权利要求书"):
            signory = signory[5:]
        # 按序号分割
        if (signory[0:2] == '1.'):
            signory_list = list(filter(None, re.split("\d+\.(?!\d)", signory)))
        elif (signory[0:2] == '1．'):
            signory_list = list(filter(None, re.split("\d+．(?!\d)", signory)))
        elif (signory[0:2] == '1、'):
            # signory_list = list(filter(None, re.split("\d+、(?!\d)", signory)))
            signory_list = [signory[2:]]
        elif (signory[0:2] == '[权'):
            signory_list = list(filter(None, re.split("\[权利要求\d+\]", signory)))
        else:
            signory_list = [signory]
    return signory_list

def signory_analysis(signory_items):
    analysis_res = []
    for signory_item in signory_items:
        analysis_res.append(signory_item_analysis(signory_item))
    return analysis_res

def signory_item_analysis(signory_item):
    # 1.recall relevant signory items 2. extract and compare
    relevant_signory_ids = get_relevant_id_list("signory", "signory", signory_item, limit=10)
    relevant_signorys = get_sig_by_id(relevant_signory_ids)
    ans_result = []
    for sig in relevant_signorys:
        ans_result.append(novelty_compare(signory_item, sig["signory_seg"]))
    return  ans_result
