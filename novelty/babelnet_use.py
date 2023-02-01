import io
import os


import babelnet as bn
from babelnet.language import Language
from babelnet.data.relation import BabelPointer

'''
byl = bn.get_synsets('硝酸钾', from_langs=[Language.ZH])
b1 = byl[0]
print(byl)
print(byl[0].lemmas(Language.ZH))

#CLASS BabelSynset,获取类别
#例子：氢氧化钠类别 [BNCAT:ZH:潮解物质, BNCAT:ZH:家用化学品, BNCAT:ZH:氢氧化物, BNCAT:ZH:钠化合物, BNCAT:ZH:腐蝕性化學品]
#分类
cate = byl[0].categories(Language.ZH)
print(cate[0].value)
'''
class Babeluse:
    def __init__(self,relation_num=100):
        self.relation_num =relation_num
        #relation_num用来规定到底找有关这个词的多少个相关关系
        #因为相关词语按照相关程度从高到低排序

    def category(self,word):#查找该词所属类别
        synset = bn.get_synsets(word, from_langs=[Language.ZH])
        cate = []
        if len(synset)!= 0:
            for i in synset:
                temp = i.categories(Language.ZH)
                for j in temp:
                    if j.value not in cate:
                        cate.append(j.value)
        return cate

    def another_name(self,word):#查找该词的别名
        synset = bn.get_synsets(word, from_langs=[Language.ZH])
        name = []

        if synset == []:
            return name
        for i in synset:
            temp = i.lemmas(Language.ZH)
            for j in temp:
                if j.lemma not in name:
                    name.append(j.lemma)
        return name

    def re_synset(self,word):#查找该词的synset
        synset = bn.get_synsets(word, from_langs=[Language.ZH])
        return synset

    def domain_name_Chinese(self,word):
        #该词的中文含义
        other = "其他"
        dic = {}
        dic["ANIMALS"] = "动物学"
        dic["ART_ARCHITECTURE_AND_ARCHAEOLOGY"]="艺术"
        dic["BIOLOGY"]="生物学"
        dic["BUSINESS_INDUSTRY_AND_FINANCE"]="商业与金融"
        dic["CHEMISTRY_AND_MINERALOGY"]="化学与矿物"
        dic["COMMUNICATION_AND_TELECOMMUNICATION"]="通信与电报"
        dic["COMPUTING"]="计算机科学"
        dic["CRAFT_ENGINEERING_AND_TECHNOLOGY"]="工艺品工程与技术"
        dic["CULTURE_ANTHROPOLOGY_AND_SOCIETY"]="社会学与人类学"
        dic["EDUCATION_AND_SCIENCE"]="教育学"
        dic["EMOTIONS_AND_FEELINGS"]="情感与感知"
        dic["ENVIRONMENT_AND_METEOROLOGY"]="自然环境与天气学"
        dic["FARMING_FISHING_AND_HUNTING"]="农业与狩猎"
        dic["FOOD_DRINK_AND_TASTE"]="饮食"
        dic["GEOGRAPHY_GEOLOGY_AND_PLACES"]="地理与地质学"
        dic["HEALTH_AND_MEDICINE"]="健康与医疗学"
        dic["HERALDRY_HONORS_AND_VEXILLOLOGY"]="军械"
        dic["HISTORY"]="考古学"
        dic["LANGUAGE_AND_LINGUISTICS"]="语言学"
        dic["LAW_AND_CRIME"]="法律与犯罪学"
        dic["LITERATURE_AND_THEATRE"]="文学与戏剧学"
        dic["MATHEMATICS_AND_STATISTICS"]="数学与统计学"
        dic["MEDIA_AND_PRESS"]="媒体新闻学"
        dic["MUSIC_SOUND_AND_DANCING"]="音乐与舞蹈学" 
        dic["NAVIGATION_AND_AVIATION"]="航海与航空学"
        dic["NUMISMATICS_AND_CURRENCIES"]="货币学"
        dic["PHYSICS_AND_ASTRONOMY"]="物理与天文学"
        dic["SOLID_LIQUID_AND_GAS_MATTER"]="物质状态"
        dic["WARFARE_VIOLENCE_AND_DEFENSE"]="战争暴力与防御学"
        if word in dic.keys():
            return dic[word]
        else:
            return other



    def domain(self,word):#查找该词所属领域
        synset = bn.get_synsets(word, from_langs=[Language.ZH])
        dom_list = []
        for j in synset:
            dom = j.domains
            for k,v in dom.items():
                if str(k) != "" and str(k) not in dom_list:
                    dom_list.append(str(k))

        dom_name = []
        for i in dom_list:
            temp = self.domain_name_Chinese(word)
            if temp!="" and temp not in dom_name:
                dom_name.append(temp)
        return dom_name

    def holonym(self,word):
        synsets = bn.get_synsets(word, from_langs=[Language.ZH])
        holonym_list = []

        if synsets == []:
            return holonym_list
        synset = synsets[0]
        relation = synset.outgoing_edges()
        r = relation[0]
        t = r.pointer
        #print(t.symbol)
        if t.is_holonym == True:
            rlist = r.id_target.to_synsets(languages = [Language.ZH])
            for syn in rlist:
                lemmas = syn.lemmas(Language.ZH)
                for lemma in lemmas:
                    if lemma not in holonym_list:
                        holonym_list.append(lemma)
        return holonym_list

    def hypernym(self,word):
        synsets = bn.get_synsets(word, from_langs=[Language.ZH])
        hypernym_list = []

        if synsets == []:
            return hypernym_list
        synset = synsets[0]
        relation = synset.outgoing_edges()

        for r in relation:
            t = r.pointer
            if t.is_hypernym == True:
                rlist = r.id_target.to_synsets(languages=[Language.ZH])
                for syn in rlist:
                    lemmas = syn.lemmas(Language.ZH)
                    for lemma in lemmas:
                        if lemma not in hypernym_list:
                            hypernym_list.append(lemma.lemma)
        # r = relation[0]
        # t = r.pointer
        # #必须找第一个
        # if t.is_hypernym == True:
        #     rlist = r.id_target.to_synsets(languages = [Language.ZH])
        #     for syn in rlist:
        #         lemmas = syn.lemmas(Language.ZH)
        #         for lemma in lemmas:
        #             if lemma not in hypernym_list:
        #                 hypernym_list.append(lemma.lemma)
        return hypernym_list

    def hyponymy(self,word):
        synsets = bn.get_synsets(word, from_langs=[Language.ZH])
        hyponymy_list = []

        if synsets == []:
            return hyponymy_list
        synset = synsets[0]
        relation = synset.outgoing_edges()

        for r in relation:
            t = r.pointer
            if t.is_hyponymy == True:
                rlist = r.id_target.to_synsets(languages=[Language.ZH])
                for syn in rlist:
                    lemmas = syn.lemmas(Language.ZH)
                    for lemma in lemmas:
                        if lemma not in hyponymy_list:
                            hyponymy_list.append(lemma.lemma)

        # r = relation[0]
        # t = r.pointer
        # #必须找第一个
        # if t.is_hyponymy == True:
        #     rlist = r.id_target.to_synsets(languages = [Language.ZH])
        #     for syn in rlist:
        #         lemmas = syn.lemmas(Language.ZH)
        #         for lemma in lemmas:
        #             if lemma not in hyponymy_list:
        #                 hyponymy_list.append(lemma.lemma)
        return hyponymy_list

    def meronym(self,word):
        synsets = bn.get_synsets(word, from_langs=[Language.ZH])
        meronym_list = []
        synset = synsets[0]
        relation = synset.outgoing_edges()
        r = relation[0]
        t = r.pointer
        #必须找第一个
        if t.is_meronym == True:
            rlist = r.id_target.to_synsets(languages = [Language.ZH])
            for syn in rlist:
                lemmas = syn.lemmas(Language.ZH)
                for lemma in lemmas:
                    if lemma not in meronym_list:
                        meronym_list.append(lemma)
        return meronym_list

    def get_related(self,word):
        synsets = bn.get_synsets(word, from_langs=[Language.ZH])
        relate_list = {}

        if synsets == []:
            return relate_list
        synset = synsets[0]
        relation = synset.outgoing_edges()
        i = 0
        for r in relation:
            t = r.pointer
            #print(t.relation_name)
            rlist = r.id_target.to_synsets(languages = [Language.ZH])
            temp = []
            for syn in rlist:
                lemmas = syn.lemmas(Language.ZH)
                for lemma in lemmas:
                    if lemma not in temp:
                        temp.append(lemma.lemma)
            if len(temp) == 0:
                continue
            i += 1
            if i >= self.relation_num:
                break
            relate_list[t.relation_name] = relate_list[t.relation_name] + temp if t.relation_name in relate_list else temp
        return relate_list
        #形式["hypernym",[[List]属于hypernym的一堆词]]
