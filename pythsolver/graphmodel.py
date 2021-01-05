# sudo apt install graphviz
# !pip install graphviz
# https://github.com/xflr6/graphviz

from graphviz import Graph


def drawgraph(nodes, internal_links, external_links, sources):
    graph = Graph(comment='thermal model')

    for node in nodes:
        graph.node(node[0], node[0] + f' ({node[1]} J/K)',
                shape='rectangle')

    for src in sources.keys():
        graph.node(src, src, shape='circle')


    for link in internal_links:
        graph.edge(link[0], link[1], f'{link[2]} W/K',
                fontsize='9')

    for link in external_links:
        if link[2]:
            label = f'{link[2]} W/K'
        else:
            label = None
        graph.edge(link[0], link[1], label,
                fontsize='9', shape='normal', side='l')

    #dot.edges(['AB', 'AL'])
    #dot.edge('B', 'L', constraint='false')

    return graph