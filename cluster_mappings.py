import os
import json
import csv
import requests
import urllib.parse
import pickle
import glob  

key_clusters = [2,1,94,105]

with open('data/gene_names.pkl', 'rb') as handle:
    translator_gene_names = pickle.load(handle)

genename2ncbicurie = {i[0]:i[1] for i in translator_gene_names}

with open('data/compound_names.pkl', 'rb') as handle:
    translator_compound_names = pickle.load(handle)

samplename2pubchemcurie = {i[0]:i[1] for i in translator_compound_names}

candidate_data = []
with open("data/tox21_cluster_compound_target_candidates.csv") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if int(row['cluster']) in key_clusters:
            resolved_cid = samplename2pubchemcurie.get(row['sample_name'])
            if resolved_cid:
                row['compound_node_id'] = resolved_cid
            else:
                row['compound_node_id'] = 'PUBCHEM.COMPOUND{0}'.format(row['pubchem_cid'])
            
            row['gene_node_id'] = genename2ncbicurie.get(row['target_gene'])
            candidate_data.append(row)


with open("data/tox21_candidate_data_with_node_id.csv",'w') as ofile:
    reader = csv.DictWriter(ofile,fieldnames=[i for i in candidate_data[0].keys()])
    reader.writeheader()
    for crow in candidate_data:
        reader.writerow(crow)




print(candidate_data)