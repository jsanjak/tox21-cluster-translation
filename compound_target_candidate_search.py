import os
import json
import csv
import requests
import urllib.parse
import pickle
import glob

from kgx.transformer import Transformer
from kgx.validator import Validator
from bmt import Toolkit

from translatorpy.trapigraph import TrapiGraph
from translatorpy.translatorquery import TranslatorQuery
from translatorpy import utilities as translator_util
from joblib import Parallel, delayed


def node2kgx(nid,node,biolink_classes):
    
    kgx_node = {
        'id':nid,
        'name':node.get('name'),
        'attributes':node.get('attributes')
    }
    
    node_cats = node.get('categories')
    
    named_things = [i for i in node_cats if i in biolink_classes]
    
    if len(named_things) > 0:
        kgx_node['category'] = named_things
    else:
        kgx_node['category'] = ['biolink:NamedThing']
    
    return kgx_node
    
def edge2kgx(eid,edge):
    
    kgx_edge = {
        'id':eid,
        'subject': edge.get('subject'),
        'predicate': edge.get('predicate'),
        'object': edge.get('object')
    }
    
    attr = edge.get('attributes')

    rel_attr = [i['value'] for i in attr if i['attribute_type_id']=='biolink:relation']
    if len(rel_attr)>0:
        kgx_edge['relation'] = rel_attr[0]
    else:
        kgx_edge['relation'] = None
    
    return kgx_edge


def trapi2kgx(kg,biolink_classes):
    
    kgx = {}
    kgx['nodes'] = [node2kgx(nid,node,biolink_classes) for nid,node in kg['nodes'].items()]
    kgx['edges'] = [edge2kgx(eid,edge) for eid,edge in kg['edges'].items()]
    
    return kgx

def myquery(target_candidate,samplename2pubchemcurie,genename2ncbicurie,biolink_classes):
    
    try:
        if target_candidate['sample_name'] in samplename2pubchemcurie:
            compound=samplename2pubchemcurie[target_candidate['sample_name']]
        else:
            cid = target_candidate['pubchem_cid']
            compound = f'PUBCHEM.COMPOUND:{cid}'    
        gene = genename2ncbicurie[target_candidate['target_gene']]
        direct_edge_list = [[compound,gene,'biolink:related_to']]
        indirect_edge_list = [[compound,'biolink:NamedThing','biolink:related_to'],['biolink:NamedThing',gene,'biolink:related_to']]
        node_categories = {compound:['biolink:ChemicalEntity'],gene:['biolink:Gene']}
        #candidate_direct_trapi = TrapiGraph(direct_edge_list,format='SOP',node_data=node_categories)
        candidate_indirect_trapi = TrapiGraph(indirect_edge_list,format='SOP',node_data=node_categories)

        myquery = TranslatorQuery()
        myquery.query(candidate_indirect_trapi,delay=30)

        json_files = []
        for result in myquery.results:
            message =  myquery.results[result]['message'].get('results')

            if message is not None:
                kg = translator_util.getpath(myquery.results[result],["message","knowledge_graph"])
                kgx = trapi2kgx(kg,biolink_classes)
                
                json_fname = "data/kgx_files/{0}_{1}_{2}.json".format(target_candidate['sample_name'],target_candidate['target_gene'],result)
                json_files.append(json_fname)
                with open(json_fname,encoding='utf-8',mode='w') as kgx_file:
                    json.dump(kgx,kgx_file,ensure_ascii=False, indent=2)

        if len(json_files) > 0:
            input_args = {'filename': json_files, 'format': 'json'}
            output_args = {'filename': "data/kgx_files/{0}_{1}.tsv".format(target_candidate['sample_name'],target_candidate['target_gene']), 'format': 'tsv'}
            t = Transformer()
            t.transform(input_args=input_args, output_args=output_args)
            for fname in json_files:
                os.remove(fname)

        return 0
    except Exception as e:
        print(e)
        return 1

def main():

    key_clusters = [2,1,94,105]

    candidate_data = []
    with open("data/tox21_cluster_compound_target_candidates.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if int(row['cluster']) in key_clusters:
                candidate_data.append(row)

    all_candidate_genes = set([i['target_gene'] for i in candidate_data])
    translator_gene_names = translator_util.translate_node_name(all_candidate_genes,'NCBIGene')
    
    with open('data/gene_names.pkl','wb') as handle:
        pickle.dump(translator_gene_names,handle,protocol=pickle.HIGHEST_PROTOCOL)

    #with open('data/gene_names.pkl', 'rb') as handle:
    #    translator_gene_names = pickle.load(handle)

    genename2ncbicurie = {i[0]:i[1] for i in translator_gene_names}

    all_candidate_compounds = set([i['sample_name'] for i in candidate_data])
    translator_compound_names = translator_util.translate_node_name(all_candidate_compounds,'PUBCHEM.COMPOUND')

    with open('data/compound_names.pkl', 'wb') as handle:
        pickle.dump(translator_compound_names,handle,protocol=pickle.HIGHEST_PROTOCOL)

    #with open('data/compound_names.pkl', 'rb') as handle:
    #    translator_compound_names = pickle.load(handle)

    samplename2pubchemcurie = {i[0]:i[1] for i in translator_compound_names}

    tk = Toolkit()
    biolink_classes = ["biolink:" + i.title().replace(" ","") for i in tk.get_descendants('named thing')]

    query_succcess = Parallel(n_jobs=-1)(delayed(myquery)(target_candidate,samplename2pubchemcurie,genename2ncbicurie,biolink_classes) for target_candidate in candidate_data)

if __name__=="__main__":
    main()
