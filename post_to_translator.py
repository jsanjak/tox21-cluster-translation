import json

from translatorpy.trapigraph import TrapiGraph
from translatorpy.translatorquery import TranslatorQuery

def main():

    chemical_to_all_genes = [['PUBCHEM.COMPOUND:468595','biolink:Gene','biolink:related_to']]
    chemical_to_one_gene = [['PUBCHEM.COMPOUND:468595','NCBIGene:2064','biolink:related_to']]

    node_categories = {
        'PUBCHEM.COMPOUND:468595':['biolink:ChemicalEntity'],
        'NCBIGene:2064':['biolink:Gene']
    }

    trapi_graph_all_genes = TrapiGraph(chemical_to_all_genes,format='SOP',node_data=node_categories)
    print(trapi_graph_all_genes.query)

    trapi_graph_one_gene = TrapiGraph(chemical_to_one_gene,format='SOP',node_data=node_categories)
    print(trapi_graph_one_gene.query)

    myquery = TranslatorQuery()
    myquery.query(trapi_graph_one_gene)
    print(myquery.arax_url)

if __name__=="__main__":
    main()