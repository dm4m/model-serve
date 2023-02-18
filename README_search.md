# 修改内容

## respository/milvus_sources.py

增加了get_relevant_all_field_results类，该类主要目的是返回查询所有值（包括向量）

## services/search_service.py

增加了patent_neural_search中对查询all_field的情况的处理，与milvus_sources.py对应，它的返回值并没有用jsonify进行处理

修改了search_by_patent类，其输出为list，即候选文档集的专利id

## services/search_classes.py

该新文件用于支持 search_by_patent，包含了向量编码、结果聚合、重排三个功能函数


