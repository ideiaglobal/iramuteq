

import codecs
import os
import json
from random import randint


#pathout = '/home/pierre/fac/lerass/charlie/charliehebdo-0107-0112-corpus_fr_com_corpus_3/charlie_0712_religion_1/charliehebdo-0107-0112-corpus_fr_com_simitxt_1'
#edgesfile = os.path.join(pathout, 'edges.csv')
#nodesfile = os.path.join(pathout,'nodes.csv')
#jsonout = os.path.join(pathout,'network.json')

class GraphToJson :
    def __init__(self, nodesfile, edgesfile, jsonout, parametres = {}):

        with codecs.open(edgesfile, 'r', 'utf8') as f :
            content = f.read()
        content = content.replace('"', '')
        content = content.splitlines()
        try :
            titles_edges = content.pop(0)
            titles_edges = titles_edges.split('\t')
            edges = [line.split('\t') for line in content]
        except :
            edges = None
            
        with codecs.open(nodesfile, 'r', 'utf8') as f :
            content = f.read()
        content = content.replace('"','')
        content = content.splitlines()
        titles = content.pop(0)
        titles = titles.split('\t')
        #titles.insert(0,'')

        xr = titles.index('x')
        yr = titles.index('y')
        try :
            zr = titles.index('z')
        except :
            zr = None
        wr = titles.index('weight')
        try :
            r = titles.index('r')
            g = titles.index('g')
            b = titles.index('b')
        except :
            r = None
        ni = titles.index('name')

        nodes = [line.split('\t') for line in content]

        graph = {'edges': [], 'nodes' : {}}
        
        we = titles_edges.index('weight')
        if edges is not None :
            for edge in edges :
                graph['edges'].append({'source' : edge[0], 'target' : edge[1], 'weight' : edge[we]})
        
        
        coefcoord = parametres.get('coefcoord', 1)
        coefweight = parametres.get('coefweight', 1)
        
        
        for node in nodes :
            if zr is not None :
                graph['nodes'][node[ni]] = {"location" : [float(node[xr])*coefcoord, float(node[yr])*coefcoord, float(node[zr])*coefcoord], 'weight' : float(node[wr])/coefweight, 'color': (int(node[r]),int(node[g]),int(node[b]))}
            else :
                x = parametres.get('randomx', 0)
                if x :
                    x = randint(-150,150)
                graph['nodes'][node[ni]] = {"location" : [ x, float(node[xr]), float(node[yr])], 'weight' : float(node[wr]), 'color': (int(node[r]),int(node[g]),int(node[b]))}

        with open(jsonout, 'w') as f :
            json.dump(graph, f)

if __name__ == '__main__' :
    GraphToJson('/home/pierre/workspace/iramuteq/dev/blender-graphs/nodes.csv', '/home/pierre/workspace/iramuteq/dev/blender-graphs/edges.csv', '/home/pierre/workspace/iramuteq/dev/blender-graphs/L2_L2.json', {})