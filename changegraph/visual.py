import graphviz as gv

from pyflowgraph.models import Node
from changegraph.models import ChangeGraph, ChangeNode


def _get_label_and_attrs(node):
    label = f'{node.label}'
    attrs = {'shape': 'ellipse'}

    if node.kind == ChangeNode.Kind.DATA_NODE:
        attrs['shape'] = 'ellipse'
    elif node.kind == ChangeNode.Kind.OPERATION_NODE:
        attrs['shape'] = 'box'
    elif node.kind == ChangeNode.Kind.CONTROL_NODE:
        attrs['shape'] = 'diamond'

    if node.version == Node.Version.BEFORE_CHANGES:
        attrs['color'] = 'red2'  # colors on https://www.graphviz.org/doc/info/colors.html
    else:
        attrs['color'] = 'green4'

    return label, attrs


def _get_nodes_digraph(nodes: set, file_name, separate_mapped=True):
    vg = gv.Digraph(name=file_name, format='pdf')

    used = {}
    for node in nodes:
        if used.get(node):
            continue

        if separate_mapped and node.mapped and node.mapped in nodes:
            label, attrs = _get_label_and_attrs(node)
            mapped_label, mapped_attrs = _get_label_and_attrs(node.mapped)

            used[node] = used[node.mapped] = True

            s = gv.Digraph(f'subgraph: {node} to {node.mapped}')
            s.node(f'{node}', label=label, _attributes=attrs)
            s.node(f'{node.mapped}', label=mapped_label, _attributes=mapped_attrs)

            s.graph_attr.update(rank='same')
            vg.subgraph(s)
        else:
            label, attrs = _get_label_and_attrs(node)
            vg.node(f'{node}', label=label, _attributes=attrs)

    for node in nodes:
        for edge in node.in_edges:
            if edge.node_from not in nodes:
                continue

            label = edge.label
            attrs = {}

            vg.edge(f'{edge.node_from}', f'{edge.node_to}', xlabel=label, _attributes=attrs)

    return vg


def _convert_to_visual_graph(graph: ChangeGraph, file_name: str, separate_mapped=True):
    return _get_nodes_digraph(graph.nodes, file_name, separate_mapped=separate_mapped)


def export_graph_image(graph: ChangeGraph, path: str = 'change-graph'):
    visual_graph = _convert_to_visual_graph(graph, path.split('/')[-1])
    visual_graph.render(path)


def print_out_nodes(nodes: set, path: str = 'images/nodes'):
    visual_graph = _get_nodes_digraph(nodes, path.split('/')[-1])
    visual_graph.render(path)