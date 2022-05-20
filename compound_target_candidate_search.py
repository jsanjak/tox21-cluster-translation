import json
import csv
import requests
import urllib.parse
import pickle

from translatorpy.trapigraph import TrapiGraph
from translatorpy.translatorquery import TranslatorQuery
from translatorpy import utilities as translator_util
from joblib import Parallel, delayed

def myquery(target_candidate,samplename2pubchemcurie,genename2ncbicurie):
    
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
        myquery.to_tsv("data/translator_results/{0}_{1}.tsv".format(target_candidate['sample_name'],target_candidate['target_gene']))

        return 0
    except:
        return 1

def main():

    key_clusters = [2] #,1,94,105]

    candidate_data = []
    with open("data/tox21_cluster_compound_target_candidates.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if int(row['cluster']) in key_clusters:
                candidate_data.append(row)

    all_candidate_genes = set([i['target_gene'] for i in candidate_data])
    #translator_gene_names = translator_util.translate_node_name(all_candidate_genes,'NCBIGene',cutoff=True)
    with open('data/gene_names.pkl', 'rb') as handle:
        translator_gene_names = pickle.load(handle)

    genename2ncbicurie = {i[0]:i[1] for i in translator_gene_names}

    all_candidate_compounds = set([i['sample_name'] for i in candidate_data])
    #translator_compound_names = translator_util.translate_node_name(all_candidate_compounds,'PUBCHEM.COMPOUND')

    #with open('data/compound_names.pkl', 'wb') as handle:
    #    pickle.dump(translator_compound_names,handle,protocol=pickle.HIGHEST_PROTOCOL)

    with open('data/compound_names.pkl', 'rb') as handle:
        translator_compound_names = pickle.load(handle)

    samplename2pubchemcurie = {i[0]:i[1] for i in translator_compound_names}

    query_succcess = Parallel(n_jobs=-1)(delayed(myquery)(target_candidate,samplename2pubchemcurie,genename2ncbicurie) for target_candidate in candidate_data)

    print(query_succcess) 

if __name__=="__main__":
    main()