from .babelnet_use import Babeluse
import os
current_work_dir = os.path.dirname(__file__)
# 假设配置文件和该python文件在同一目录下
os.environ['BABELNET_CONF'] = current_work_dir + "babelnet_conf.yml"


bu = Babeluse(20)
word = '铜'
# word = input()

cate = bu.category(word)
print("cate:")
print(cate)

another_name = bu.another_name(word)
print("another_name:")
print(another_name)


domain = bu.domain(word)
print("domain:")
print(domain)

# 全名
holonym = bu.holonym(word)
print("holonym:")
print(holonym)

# 上位词
hypernym = bu.hypernym(word)
print("hypernym:")
print(hypernym)

# 下位词
hyponymy = bu.hyponymy(word)
print("hyponymy:")
print(hyponymy)

# 分词
meronym = bu.meronym(word)
print("meronym:")
print(meronym)

get_related = bu.get_related(word)
print("get_related:")
print(get_related)