from .utilities import translate_node_name
from collections import OrderedDict

class TrapiGraph():

    def __init__(self,edge_list,format="SOP",node_data=None) -> None:
        self.query = {
            "message":{
                "query_graph":{
                    "edges":{},
                    "nodes":{}
                }
            }
        }
        self.node_set = OrderedDict()
        self.construct_trapi_message(edge_list,format,node_data)

    def __validate(self):
        """
        A private method to validate graph structure in case of misspecified input.
        """
        pass

    def __set_nodes(self,node_data) -> None:
        """
        A private method to set the nodes element of the trapi query graph
        """
        for node in self.node_set:
            
            node_cat = ['biolink:NamedThing']
            nid = [node]
            if node_data is not None:
                if node in node_data:
                    node_cat = node_data[node]
            
            if 'biolink' in node:
                node_cat = [node]

                self.query['message']['query_graph']['nodes'][self.node_set[node]] = {
                    'categories':node_cat
                }
            else:
                self.query['message']['query_graph']['nodes'][self.node_set[node]] = {
                    'ids':nid,
                    'categories':node_cat
                }
    
    def __set_edge(self,i,subj,obj,predicates) -> None:
        """
        A private method to set a single trapi query graph edge
        """
        for n in [subj,obj]:
            if n not in self.node_set:
                if len(self.node_set)==0:
                    self.node_set[n] = f'n00'
                else:
                    nid = int(list(self.node_set.items())[len(self.node_set)-1][1][2])
                    self.node_set[n] = f'n0{nid+1}'
        
        self.query['message']['query_graph']['edges'][f'e0{i}'] = {
                    'subject': self.node_set[subj],
                    'object': self.node_set[obj],
                    'predicates':predicates
                    }
        
        
    def __set_edges(self,edge_list,format='SOP') -> None:
        """
        A private method to set the edges element of the trapi query graph in
        either subject-object-predicate or subject-predicate-object format.
        """

        if format == "SOP":
            #clear old edges in case of reuse
            self.query['message']['query_graph']['edges'] = {}
            for i,edge in enumerate(edge_list):
                self.__set_edge(i,edge[0],edge[1],edge[2:])

        elif format == "SPO":
            #clear old edges in case of reuse
            self.query['message']['query_graph']['edges'] = {}
            for i,edge in enumerate(edge_list):
                self.__set_edge(i,edge[0],edge[2],[edge[1]])
        else:
            raise ValueError("Formats accepted are SOP (Subject-Object-Predicate) and SPO (Subject-Predicate-Object)")


    def construct_trapi_message(self,edge_list,format="SOP",node_data=None):
        """
        A public method for constructing a properly formatted trapi message from a 
        simplified edge list. Node information is optional, as the nodes can be deduced from the edgelist.
        However, nodes deduced from edge list will be assumed to be of the biolink:NamedThing category.
        """
        
        try:
            self.__set_edges(edge_list,format)
    
            self.__set_nodes(node_data)
        
            self.__validate()
        except:
            print("Invalid edge and/or node list")



    #Method to construct a simple one hop query.  Default values are set to the most general form
    #def construct_query(id0, type0=["biolink:NamedThing"],type1=["biolink:NamedThing"],
    #                    predicates=["biolink:related_to"]):
    #    with open('template.json','r') as inf:
    #        query = json.load(inf)
    #        query["message"]["query_graph"]["edges"]["e01"]["predicates"]=predicates
    #        query["message"]["query_graph"]["nodes"]["n0"]["ids"]=id0
    #        #query["message"]["query_graph"]["nodes"]["n1"]["ids"]=id1
    #        query["message"]["query_graph"]["nodes"]["n0"]["categories"]=type0
    #        query["message"]["query_graph"]["nodes"]["n1"]["categories"]=type1
    #        return query