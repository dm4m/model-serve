import re
import pdfplumber

def signory_extract():
    signory = ""
    with pdfplumber.open("sample.pdf") as pdf:
        for page in pdf.pages:
            cur_text = page.extract_text().replace("　", "").replace(" ", "")
            if "权利要求书" in cur_text and "说明书" not in cur_text:
                signory += cur_text
    print(signory)
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

if __name__ == '__main__':
    ll = signory_split(signory_extract())
    print(ll)
