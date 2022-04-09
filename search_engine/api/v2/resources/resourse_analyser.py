from string import Template
from search_engine import search_omero_app
from datetime import datetime
import time
import json
from utils import resource_elasticsearchindex

key_number_search_template=Template('''{"size":0,"aggs":{"value_search":{"nested":{"path":"key_values"},
         "aggs":{"value_filter":{"filter":{"terms":{"key_values.name.keyword":["$key"]}},
               "aggs":{"required_values":{"cardinality":{"field":"key_values.value.keyvalue","precision_threshold":4000
                     }}}}}}}}
                     ''')

search_bey_value_only= Template('''
                    {"query":{"bool":{"must":[{"nested":{"path":"key_values","query":{"bool":{"must":[{"wildcard":
                                                        {"key_values.value.keyvaluenormalize":"*eLa*"}}]}}}}]}}}
                         ''')
'''
The number of returned value is limited to 9999
I will add paging to these statment to pull all the results
'''
value_number_search_template = Template('''
            {"size": 0,"aggs": {"name_search": {"nested": {"path": "key_values"},"aggs": {"value_filter": {"filter": {
                "terms": {"key_values.value.keyvaluenormalize": ["$value"]}},"aggs": {"required_name": {"cardinality": {
                    "field": "key_values.name.keyword","precision_threshold": 4000}}}}}}}}
                    ''')

value_search_template=Template('''{"size": 0,"aggs": {"name_search": {"nested": {"path": "key_values"},"aggs": {"value_filter": {
          "filter": {"terms": {"key_values.value.keyvaluenormalize": ["$value"]}},"aggs": {"required_name": {
              "terms": {"field": "key_values.name.keyword","size": 9999}}}}}}}}
              ''')

value_search_contain_template = Template('''{"size": 0,"aggs": {"name_search": {"nested": {"path": "key_values"},
          "aggs": {"value_filter": {"terms": {"field":"key_values.value.keyvaluenormalize","include": ".*$value.*"
              },"aggs": {"required_name": {"terms": {"field": "key_values.name.keyword","size": 9999}}}}}}}}
    ''')
key_search_template=Template('''{"size": 0,"aggs": {"name_search": {"nested": {"path": "key_values"},"aggs": {"value_filter": {
          "filter": {"terms": {"key_values.name.keyword": ["$key"]}},"aggs": {"required_values": {
              "terms": {"field": "key_values.value.keyvaluenormalize","size": 9999}}}}}}}}
              ''')


values_for_key_template=Template('''{"size":0,
   "aggs":{"name_search":{"nested":{ "path":"key_values"},"aggs":{"value_filter":{"filter":{
                  "terms":{"key_values.name.keyword":["$key"]}},"aggs":{"required_values":{
                     "terms":{"field":"key_values.value.keyvaluenormalize","include": {"partition": "$cur","num_partitions": "$total"},
                            "size":10000 }}}}}}}}
                            ''')

def format_the_results(results):
    pass

def search_index_for_value(e_index, query):
    '''
    Perform search the elastcisearch using value and return all the key values whihch this value has been used, it will include thenumber of records
    It relatively slow but I think it may be my the elasticsearcg hsting  machine
    '''

    es = search_omero_app.config.get("es_connector")
    res = es.search(index=e_index, body=query)
    return res

def search_index_for_values_get_all_buckets(e_index, query):
    '''
    Perform search the elastcisearch using value and return all the key values whihch this value has been used, it will include thenumber of records
    It relatively slow but I think it may be my the elasticsearcg hsting  machine
    '''
    page_size=9999
    bookmark=0
    query=json.loads(query)

    returened_results=[]
    es = search_omero_app.config.get("es_connector")
    res = es.count(index=e_index, body=query)
    size=res['count']
    #print ("====>>>",size)
    query['size'] = page_size
    query["sort"]= [
        {
            "_id": "asc"
        }
    ]
    #print (query)
    co=0
    while co < size:
        if co!=0:
            query["search_after"] = bookmark
        #print (bookmark)
        query['size'] = page_size
        res = es.search(index=e_index, body=query)
        returened_results.append(res)
        co+=page_size
        if len(res['hits']['hits']) == 0:
            search_omero_app.logger.info("No result is found")
            return returened_results
        bookmark = [res['hits']['hits'][-1]['sort'][0]]

    return returened_results


def search_value_for_resource_(table_, value):
    '''
    send the request to elasticsearch and format the results
    '''
    res_index = resource_elasticsearchindex.get(table_)
    query=value_search_contain_template.substitute(value= value.lower())
    res = search_index_for_value(res_index, query)
    total_number=0
    returnted_results=[]
    if res.get("aggregations"):
        for bucket in res.get("aggregations").get("name_search").get("value_filter").get("buckets"):
            value=bucket.get("key")
            value_no=bucket.get("doc_count")
            for buc in bucket.get("required_name").get("buckets"):
                singe_row = {}
                returnted_results.append((singe_row))
                key = buc.get("key")
                key_no = buc.get("doc_count")
                singe_row["Attribute"]=key
                singe_row["Value"] =value
                singe_row["Number of %ss"%table_] =key_no
                total_number+=key_no
    return {"returnted_results":returnted_results, "total_number":total_number}

def get_number_of_buckets(key, res_index):
    query=key_number_search_template.substitute(key=key)
    res = search_index_for_value(res_index, query)
    number_of_buckets = res.get("aggregations").get("value_search").get("value_filter").get("required_values").get(
        "value")
    number_of_images = res.get("aggregations").get("value_search").get("value_filter").get("doc_count")
    #print (number_of_buckets, number_of_images)
    return number_of_buckets, number_of_images


def get_all_values_for_a_key(table_, key):
    res_index = resource_elasticsearchindex.get(table_)
    query = key_number_search_template.substitute(key=key)
    res = search_index_for_value(res_index, query)
    number_of_buckets = res.get("aggregations").get("value_search").get("value_filter").get("required_values").get(
        "value")
    number_of_items = res.get("aggregations").get("value_search").get("value_filter").get("doc_count")
    import math
    total=math.ceil(number_of_buckets/10000)

    co=0
    results=[]
    total_ret=0
    while co<total:
        search_omero_app.logger.info ("processing: %s / %s"%((co+1),total))
        query = values_for_key_template.substitute(key=key, total=total, cur=co)
        res = search_index_for_value(res_index,query)
        results.append (res)
        total_ret+=len(res["aggregations"]["name_search"]["value_filter"]["required_values"]["buckets"])
        co+=1
    returnted_results = []
    total_number=0
    for res in results:
        if res.get("aggregations"):
            for bucket in res.get("aggregations").get("name_search").get("value_filter").get("required_values").get(
                    "buckets"):
                value = bucket.get("key")
                value_no = bucket.get("doc_count")
                total_number += value_no
                singe_row = {}
                returnted_results.append(singe_row)
                singe_row["Attribute"] = key
                singe_row["Value"] = value
                singe_row["Number of %ss" % table_] = value_no


    return {"returnted_results":returnted_results, "total_number":total_number, "total_number_of_%s"%(table_):number_of_items,"total_number_of_buckets": len(returnted_results)}




def get_values_for_a_key(table_, key):
    '''
    search the index to get he avialble values for a key and get values number for the key
    '''
    total_number=0
    res_index = resource_elasticsearchindex.get(table_)
    number_of_buckets, number_of_images=get_number_of_buckets(key, res_index)
    query=key_search_template.substitute(key=key)
    start_time = time.time()
    res = search_index_for_value(res_index, query)
    query_time = ("%.2f" % (time.time() - start_time))
    print("TIME ...", query_time)
    returnted_results=[]
    if res.get("aggregations"):
        for bucket in res.get("aggregations").get("name_search").get("value_filter").get("required_values").get("buckets"):
            value = bucket.get("key")
            value_no = bucket.get("doc_count")
            total_number+=value_no
            singe_row = {}
            returnted_results.append(singe_row)
            singe_row["Attribute"] = key
            singe_row["Value"] = value
            singe_row["Number of %ss"%table_] = value_no
    return {"returnted_results":returnted_results, "total_number":total_number, "total_number_of_%s"%(table_):number_of_images,"total_number_of_buckets": number_of_buckets}

def prepare_search_results(results):
    returned_results=[]
    total=0
    total_number=0
    total_items=0
    number_of_buckets=0
    resource=None
    #print (len(results.get("hits").get("hits")))
    for hit in results["hits"]["hits"]:
        #print (total,"/",len(results["hits"]["hits"]))
        row={}
        returned_results.append(row)
        res=hit["_source"]
        #print(res.keys())
        row["Attribute"] = res["Attribute"]
        row["Value"] = res["Value"]
        resource=res.get("resource")
        row["Number of %ss" % resource] = res.get("items_in_the_bucket")
        total_number=res["total_items_in_saved_buckets"]
        number_of_buckets=res["total_buckets"]
        total_items=res["total_items"]
    return {"returnted_results": returned_results, "total_number": total_number,
            "total_number_of_%s" % (resource): total, "total_number_of_buckets": number_of_buckets, "total_items":total_items}

def prepare_search_results_buckets(results_):
    returned_results=[]
    total=0
    total_number=0
    total_items=0
    number_of_buckets=0
    resource=None
    #print (len(results.get("hits").get("hits")))
    for results in results_:
        for hit in results["hits"]["hits"]:
            #print (total,"/",len(results["hits"]["hits"]))
            row={}
            returned_results.append(row)
            res=hit["_source"]
            row["Attribute"] = res["Attribute"]
            row["Value"] = res["Value"]
            resource=res.get("resource")
            row["Number of %ss" % resource] = res.get("items_in_the_bucket")
            total_number=res["total_items_in_saved_buckets"]
            number_of_buckets=res["total_buckets"]
            total_items=res["total_items"]
    return {"returnted_results": returned_results, "total_number": total_number,
            "total_number_of_%s" % (resource): total, "total_number_of_buckets": number_of_buckets, "total_items":total_items}

def query_cashed_bucket(name ,resource, es_index="key_value_buckets_information"):
    #toz fikoum
    if resource !="all":
        query=key_values_buckets_template.substitute(name=name, resource=resource)
        res=search_index_for_values_get_all_buckets(es_index, query)
        returned_results= prepare_search_results_buckets(res)
        return returned_results
    else:
        returned_results={}
        for table in resource_elasticsearchindex:
            query = key_values_buckets_template.substitute(name=name, resource=table)
            res = search_index_for_values_get_all_buckets(es_index, query)
            returned_results[table]= prepare_search_results_buckets(res)
        return returned_results
        

def query_cashed_bucket_value(value, es_index="key_value_buckets_information"):
    query=value_all_buckets_template.substitute(value=value)
    res=search_index_for_value(es_index, query)
    return prepare_search_results(res)

def search_value_for_resource(table_, value, es_index="key_value_buckets_information"):
    '''
    send the request to elasticsearch and format the results
    '''
    if value:
        value=value.strip().lower()
    #query=value_all_buckets_template.substitute(value=value)
    if table_!="all":
        query=resource_key_values_buckets_template.substitute(value=value, resource='image')
        res = search_index_for_value(es_index, query)
        return prepare_search_results(res)
    else:
        returned_results = {}
        for table in resource_elasticsearchindex:
            #res = es.count(index=e_index, body=query)
            query = resource_key_values_buckets_template.substitute(value=value, resource=table)

            res = search_index_for_value(es_index, query)
            returned_results[table] = prepare_search_results(res)
        return returned_results

def get_keys_for_value(table, key):
    pass

'''
Search using key and resourse'''
key_values_buckets_template= Template ('''{"query":{"bool":{"must":[{"bool":{
                  "must":{"match":{"Attribute.keyname":"$name"}}}},{
                 "bool": {"must": {"match": {"resource.keyresource": "$resource"}}}}]}}} ''')

#"fields": ["Attribute","Value","items_in_the_bucket","total_items_in_saved_buckets","total_buckets","total_items"],"_source": false,
ss=Template ('''{"query":{"bool":{"must":[{"bool":{
                      "must":{"match":{"Attribute.keyname":"$name"}}}},{"bool": {
                     "must": {"match": {"resource.keyresource": "$resource"}}}}]}} ,"size": 9999}''')
'''
Search using value and resourse'''
key_values_search_buckets_template= Template ('''{"query":{"bool":{"must":[{"bool":{
                  "must":{"match":{"Value.keyvalue":"$value"}}}},{
                 "bool": {"must": {"match": {"resource.keyresource": "$resource"}}}}]}},"size": 9999} ''')

'''
Search using value or part of value and return all the posible mathes '''

value_all_buckets_template=Template('''{"query":{"bool":{"must":[{"bool":{
                  "must":{"wildcard":{"Value.keyvaluenormalize":"*$value*"}}}}]}},"size": 9999}''')


resource_key_values_buckets_template= Template ('''{"query":{"bool":{"must":[{"bool":{
                  "must":{"wildcard":{"Value.keyvaluenormalize":"*$value*"}}}},{
                 "bool": {"must": {"match": {"resource.keyresource": "$resource"}}}}]}},  
                 "size": 9999} ''')