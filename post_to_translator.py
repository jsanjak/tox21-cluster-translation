import translatorpy
import json

def main():

    with open("json/indirect-one-hop-connection.json") as json_file:
        indirect_payload = json.load(json_file)

    pubchem_id = 468595
    ncbi_gene_id = 2064
    
    indirect_payload['message']['query_graph']['nodes']['n00']['ids'][0]='PUBCHEM.COMPOUND:{0}'.format(str(pubchem_id))
    indirect_payload['message']['query_graph']['nodes']['n02']['ids'][0]='NCBIGene:{0}'.format(str(ncbi_gene_id))

    myquery = translatorpy.TranslatorQuery()
    myquery.query(indirect_payload)
    print(myquery.arax_url)

if __name__=="__main__":
    main()