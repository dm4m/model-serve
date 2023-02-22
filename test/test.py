import json
import sys
import os
import time
from pymilvus import connections, Collection
# 如果只append不起作用，则需要增加这一行
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append('/data/gmt/model-serve/novelty')
sys.path.append('/data/gmt/model-serve/models')
sys.path.append('/data/gmt/model-serve/services')
sys.path.append('/data/gmt/model-serve/repository')

# from novelty.compare import novelty_compare
from services.search_service import search_by_patent
from repository.mysql_source import get_class_by_id
from pymilvus import utility

def test_novelty_compare():
    sovereign_content_1 = '一种炸药，其特征在于，所述炸药包括如下重量百分比的组分：'
    sovereign_content_2 = '一种陶化剂，其特征在于，该陶化剂由下列重量比例成份组成。'
    # sovereign_content_1 = '该装置由螺钉构成。'
    # sovereign_content_2 = '螺栓构成了该装置。'
    print(novelty_compare(sovereign_content_2, sovereign_content_1))

def compare_class_precise(classA,classB):
    # 用于对比两个专利的分数
    # classA、classB:[[main_class],[other_class_list]]
    score = 0
    # 主类对有6分，分类每有1对相似的+2分
    if classA[0][0] == classB[0][0]:
        score += 6

    for i in classA[1]:
        for j in classB[1]:
            if i == j:
                score += 2
            break
    return score

def eval_search_recall(filename):
    # 用于宏观地评价检索效果,test_search_by_patent
    scores = 0
    count = 0
    with open(filename,"r",encoding="utf-8") as f:
        rawdata = f.readlines()
        for i in range(0,len(rawdata),2):
            id_info = get_class_by_id(int(rawdata[i].rstrip("\n")))
            idlist = list(map(int,(rawdata[i+1].rstrip("\n")).split(" ")))
            for now_id in idlist:
                now_info = get_class_by_id(now_id)
                scores += compare_class_precise(id_info,now_info)
                count += 1
    print("平均检测分数：{}".format(scores/count))

def test_search_by_patent():
    # 单项测试
    # # patent_signory_list_1 = ["1.一种带粘合剂层的偏振膜，具备：偏振片与配置于该偏振片的至少单侧的粘合剂层； 该偏振片与该粘合剂层的距离为25μm以下； 该粘合剂层在580nm～610nm范围的波段具有吸收峰，且 该粘合剂层包含下述通式(I)或通式(II)所示化合物X：    S-CH3…(b) 式(I)中，R1、R2、R3、R4、R5、R6、R7及R8分别独立为氢原子、卤素原子、碳数1以上且20以下的取代或未取代的烷基、式(a)所示取代基或式(b)所示取代基；或 R1与R2形成由5或6个碳原子所构成的饱和环状骨架，且R3、R4、R5、R6、R7及R8分别独立为氢原子、卤素原子(优选为Cl)、碳数1以上且20以下的取代或未取代的烷基、式(a)所示取代基或式(b)所示取代基；或 R2与R3形成由5～7个碳原子所构成的饱和环状骨架，且R1、R4、R5、R6、R7及R8分别独立为氢原子、卤素原子(优选为Cl)、碳数1以上且20以下的取代或未取代的烷基、式(a)所示取代基或式(b)所示取代基；或 R5与R6形成由5或6个碳原子所构成的饱和环状骨架，且R1、R2、R3、R4、R7及R8分别独立为氢原子、卤素原子(优选为Cl)、碳数1以上且20以下的取代或未取代的烷基、式(a)所示取代基或式(b)所示取代基；或 R6与R7形成由5～7个碳原子所构成的饱和环状骨架，且R1、R2、R3、R4、R5及R8分别独立为氢原子、卤素原子(优选为Cl)、碳数1以上且20以下的取代或未取代的烷基、式(a)所示取代基或式(b)所示取代基；或 R1与R2形成由5或6个碳原子所构成的饱和环状骨架，R5与R6形成由5或6个碳原子所构成的饱和环状骨架，且R3、R4、R7及R8分别独立为氢原子、卤素原子(优选为Cl)、碳数1以上且20以下的取代或未取代的烷基、式(a)所示取代基或式(b)所示取代基；或者， R2与R3形成由5～7个碳原子所构成的饱和环状骨架，R6与R7形成由5～7个碳原子所构成的饱和环状骨架，且R1、R4、R5及R8分别独立为氢原子、卤素原子(优选为Cl)、碳数1以上且20以下的取代或未取代的烷基、式(a)所示取代基或式(b)所示取代基； 式(II)中，R4及R8分别独立为氢原子或碳数1以上且20以下的取代或未取代的烷基。","2.根据权利要求1所述的带粘合剂层的偏振膜，其中，所述偏振片为聚乙烯醇系偏振片。","3.根据权利要求1所述的带粘合剂层的偏振膜，其中，所述偏振片与所述粘合剂层直接层叠。","4.根据权利要求1所述的带粘合剂层的偏振膜，其中，所述偏振片的氧气透过率为1[cm3/(m2·24h·atm)]以下。","5.根据权利要求1所述的带粘合剂层的偏振膜，其中，所述粘合剂层的厚度为25μm以下。","6.一种图像显示设备，具备权利要求1所述的带粘合剂层的偏振膜。"]
    #     # patent_id_1 = 9531
    #     # patent_signory_list_1 = [
    #     #     "1.一种带粘合剂层的偏振膜，具备：偏振片与配置于该偏振片的至少单侧的粘合剂层； 该偏振片与该粘合剂层的距离为25μm以下； 该粘合剂层在580nm～610nm范围的波段具有吸收峰，且 该粘合剂层包含下述通式(I)或通式(II)所示化合物X：    S-CH3…(b) 式(I)中，R1、R2、R3、R4、R5、R6、R7及R8分别独立为氢原子、卤素原子、碳数1以上且20以下的取代或未取代的烷基、",
    #     #     "2.根据权利要求1所述的带粘合剂层的偏振膜，其中，所述偏振片为聚乙烯醇系偏振片。",
    #     #     "3.根据权利要求1所述的带粘合剂层的偏振膜，其中，所述偏振片与所述粘合剂层直接层叠。",
    #     #     "4.根据权利要求1所述的带粘合剂层的偏振膜，其中，所述偏振片的氧气透过率为1[cm3/(m2·24h·atm)]以下。",
    #     #     "5.根据权利要求1所述的带粘合剂层的偏振膜，其中，所述粘合剂层的厚度为25μm以下。",
    #     #     "6.一种图像显示设备，具备权利要求1所述的带粘合剂层的偏振膜。"]
    #     # # patent_id_2 = 562
    #     # # patent_signory_list_2 = ["1、一种烟花鞭炮火药彩光氧化剂，其特征在于由下列重量份额的原料混合制成：高氯酸钾30-80、硝酸钡10-40、阻燃剂10-30。"]
    #     # # patent_id_3 = 709
    #     # # patent_signory_list_3 = ["一种具有贮存期高稳定性的乳化炸药，由水相材料和油相材料及复合乳化剂组成，其特征是水相材料是以硝酸铵和乙二胺二硝酸盐为主形成的低共溶物质。"]

    # 综合数据的话取testlist里的一些内容
    avg_time = 0
    count = 0
    all_time = 0
    with open("/data/gmt/model-serve/test/test_dataset.json","r",encoding="utf-8",errors='ignore') as f:
        class_dict = json.load(f)
        for i in class_dict:
            if i["signory"] == "":
                continue
            patent_id = i["id"]
            patent_signory_list = i["signory"]
            start = time.time()
            idlist = search_by_patent(patent_signory_list)
            end = time.time()
            with open("/data/gmt/model-serve/test/test_id_HNSW.txt","a+",encoding="utf-8") as w:
                w.write(str(patent_id))
                w.write("\n")
                w.write(str(idlist[0])+" "+str(idlist[1])+" "+str(idlist[2])+"\n")
            print("origin_id:{},search_top3_id:{}".format(patent_id,idlist[0:3]))
            print("运行时间:{}s".format(round(end-start,2)))
            count += 1
            avg_time += round(end-start,2)
        # HNSW:平均26.38s/改进后平均10.56s
        # PQ:平均28.36S
        # IVF_SQ8:平均30.88s
        print("平均运行时间为:{}s".format(round(avg_time/count,2)))
        print("平均运行时间（仅检索）为:{}s".format(round(all_time/count, 2)))

    # 比较效果
    # HNSW:平均6.21分/改代码6.10分
    # PQ:平均6.11分
    # IVF_SQ8:平均6.09分
    eval_search_recall("/data/gmt/model-serve/test/test_id_HNSW.txt")


if __name__ == '__main__':
    # load_model()
    # test_get_sig_by_id()
    # models.init_app()
    # test_signory_item_analysis()
    # test_novelty_compare()
    test_search_by_patent()
    # test_mysql()
