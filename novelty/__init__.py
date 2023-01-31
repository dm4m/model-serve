
import os

current_work_dir = os.path.dirname(__file__)
# 假设配置文件和该python文件在同一目录下
os.environ['BABELNET_CONF'] = current_work_dir + "/babelnet_conf.yml"

import OpenHowNet
from novelty.sentence_parser import LtpParser
import hanlp
from .babelnet_use import Babeluse
def init_hanlp():
    dict = []
    with open(os.path.dirname(__file__)  + '/data/dict.txt', 'r') as f:
        for line in f:
            dict.append(line.strip('\n').split(',')[0])
    HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)
    HanLP['tok/fine'].dict_force = None
    HanLP['tok/fine'].dict_combine = dict
    return HanLP


hownet = OpenHowNet.HowNetDict(init_sim=True, init_babel=True)
parser = LtpParser()
HanLP = init_hanlp()
bu = Babeluse(20)

