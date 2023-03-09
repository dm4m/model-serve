import sys
# sys.path.append('/data/bwj/project/model-serve/novelty')
# sys.path.append('/data/bwj/project/model-serve/models')
# sys.path.append('/data/bwj/project/model-serve/services')
from novelty.compare import novelty_compare
# from services.search_service import search_by_patent

import time

def test_novelty_compare():
    sovereign_content_1 = '一种同时制备奥克托今和黑索今的方法，其特征在于：该方法以乙腈和三聚甲醛为原料，浓硫酸为催化剂，缩合得到TAT和TRAT的混合物；再以TAT和TRAT的混合物为原料，浓硝酸和五氧化二磷为硝化剂，硝化得到HMX和RDX的混合物，然后采用DMF络合物分离法提纯HMX和RDX，最后再采用反溶剂相分离法提纯RDX。'
    sovereign_content_2 = '一种碳膜包覆的Cu-Bi/碳纳米管复合粉体，其特征为：碳膜包覆的Cu-Bi/碳纳米管复合粉体的主要组分为：碳膜、Cu、Bi和多壁碳纳米管(MWCNT)，各种组分的含量按重量百分比计算为：碳膜：10～20％；Cu-Bi：40～55％(其中Cu：15～30％；Bi：25～40％)；MWCNT：30～45％；'

    start = time.time()
    review_opinion, words_info, words_info_str = novelty_compare(sovereign_content_2, sovereign_content_1)
    end = time.time()
    print(f"\nwords_info:\n{words_info}")
    print(f"\nwords_compare_result_str:\n{words_info_str}")
    print(f"\nreview_opinion:\n{review_opinion}")
    print("总时间：", end-start)


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
    patent_id_1 = 9531
    # patent_signory_list_1 = ["1.一种带粘合剂层的偏振膜，具备：偏振片与配置于该偏振片的至少单侧的粘合剂层； 该偏振片与该粘合剂层的距离为25μm以下； 该粘合剂层在580nm～610nm范围的波段具有吸收峰，且 该粘合剂层包含下述通式(I)或通式(II)所示化合物X：    S-CH3…(b) 式(I)中，R1、R2、R3、R4、R5、R6、R7及R8分别独立为氢原子、卤素原子、碳数1以上且20以下的取代或未取代的烷基、式(a)所示取代基或式(b)所示取代基；或 R1与R2形成由5或6个碳原子所构成的饱和环状骨架，且R3、R4、R5、R6、R7及R8分别独立为氢原子、卤素原子(优选为Cl)、碳数1以上且20以下的取代或未取代的烷基、式(a)所示取代基或式(b)所示取代基；或 R2与R3形成由5～7个碳原子所构成的饱和环状骨架，且R1、R4、R5、R6、R7及R8分别独立为氢原子、卤素原子(优选为Cl)、碳数1以上且20以下的取代或未取代的烷基、式(a)所示取代基或式(b)所示取代基；或 R5与R6形成由5或6个碳原子所构成的饱和环状骨架，且R1、R2、R3、R4、R7及R8分别独立为氢原子、卤素原子(优选为Cl)、碳数1以上且20以下的取代或未取代的烷基、式(a)所示取代基或式(b)所示取代基；或 R6与R7形成由5～7个碳原子所构成的饱和环状骨架，且R1、R2、R3、R4、R5及R8分别独立为氢原子、卤素原子(优选为Cl)、碳数1以上且20以下的取代或未取代的烷基、式(a)所示取代基或式(b)所示取代基；或 R1与R2形成由5或6个碳原子所构成的饱和环状骨架，R5与R6形成由5或6个碳原子所构成的饱和环状骨架，且R3、R4、R7及R8分别独立为氢原子、卤素原子(优选为Cl)、碳数1以上且20以下的取代或未取代的烷基、式(a)所示取代基或式(b)所示取代基；或者， R2与R3形成由5～7个碳原子所构成的饱和环状骨架，R6与R7形成由5～7个碳原子所构成的饱和环状骨架，且R1、R4、R5及R8分别独立为氢原子、卤素原子(优选为Cl)、碳数1以上且20以下的取代或未取代的烷基、式(a)所示取代基或式(b)所示取代基； 式(II)中，R4及R8分别独立为氢原子或碳数1以上且20以下的取代或未取代的烷基。","2.根据权利要求1所述的带粘合剂层的偏振膜，其中，所述偏振片为聚乙烯醇系偏振片。","3.根据权利要求1所述的带粘合剂层的偏振膜，其中，所述偏振片与所述粘合剂层直接层叠。","4.根据权利要求1所述的带粘合剂层的偏振膜，其中，所述偏振片的氧气透过率为1[cm3/(m2·24h·atm)]以下。","5.根据权利要求1所述的带粘合剂层的偏振膜，其中，所述粘合剂层的厚度为25μm以下。","6.一种图像显示设备，具备权利要求1所述的带粘合剂层的偏振膜。"]
    patent_signory_list_1 = [
        "1.一种带粘合剂层的偏振膜，具备：偏振片与配置于该偏振片的至少单侧的粘合剂层； 该偏振片与该粘合剂层的距离为25μm以下； 该粘合剂层在580nm～610nm范围的波段具有吸收峰，且 该粘合剂层包含下述通式(I)或通式(II)所示化合物X：    S-CH3…(b) 式(I)中，R1、R2、R3、R4、R5、R6、R7及R8分别独立为氢原子、卤素原子、碳数1以上且20以下的取代或未取代的烷基、",
        "2.根据权利要求1所述的带粘合剂层的偏振膜，其中，所述偏振片为聚乙烯醇系偏振片。",
        "3.根据权利要求1所述的带粘合剂层的偏振膜，其中，所述偏振片与所述粘合剂层直接层叠。",
        "4.根据权利要求1所述的带粘合剂层的偏振膜，其中，所述偏振片的氧气透过率为1[cm3/(m2·24h·atm)]以下。",
        "5.根据权利要求1所述的带粘合剂层的偏振膜，其中，所述粘合剂层的厚度为25μm以下。",
        "6.一种图像显示设备，具备权利要求1所述的带粘合剂层的偏振膜。"]
    
    # patent_id_2 = 562
    # patent_signory_list_2 = ["1、一种烟花鞭炮火药彩光氧化剂，其特征在于由下列重量份额的原料混合制成：高氯酸钾30-80、硝酸钡10-40、阻燃剂10-30。"]
    idlist_1 = search_by_patent(patent_signory_list_1)
    print("origin_id:{},search_top3_id:{}".format(patent_id_1,idlist_1[0:3]))


if __name__ == '__main__':
    # load_model()
    # test_get_sig_by_id()
    #  models.init_app()
    # test_signory_item_analysis()
    test_novelty_compare()
    # test_search_by_patent()
    # test_mysql()
