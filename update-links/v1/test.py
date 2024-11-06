import logging
import os
from collections import defaultdict
import argparse
import re
import sys
import networkx as nx
import matplotlib.pyplot as plt
sys.path.append('C:/Users/raykim/Documents/workspace/personal/workspace/toolbox/')
import common.ray_tools as ray_tools

# Set up logging
log_directory = os.path.dirname(__file__) + f'\\logs'

if not os.path.exists(log_directory):
    os.makedirs(log_directory)
logging.basicConfig(
    filename=os.path.join(log_directory, 'update_link.log'),
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Strict mode will raise an error if an anchor is not found in the target node
parser = argparse.ArgumentParser(description='Process some markdown files.')
parser.add_argument('--strict', action='store_true', help='Enable strict mode')
args = parser.parse_args()
STRICT = args.strict

class MarkdownNode:
    def __init__(self, path, root_folder_path):
        self.path = path
        self.root_folder_path = root_folder_path
        self.full_path = os.path.normpath(os.path.join(self.root_folder_path, path))
        self.anchors = self._add_anchors(self.full_path)
        self.links = set()

    def add_link(self, linked_node:'MarkdownNode', anchor:str=None):
        self.links.add((linked_node, anchor))
        
    def has_link_to(self, linked_node:'MarkdownNode') -> bool:
        return any(link[0] == linked_node for link in self.links)

    def remove_link(self, linked_node:'MarkdownNode', anchor:str=None):
        if (linked_node, anchor) not in self.links:
            raise ValueError(f"Link not found: {self.path} -> {linked_node.path}#{anchor}")
        self.links.discard((linked_node, anchor))

    def _add_anchors(self, full_path):
        with open(full_path, 'r', encoding='utf-8') as file:
            content = file.read()
            anchors_mk = re.findall(r'\{ #(.*?) \}', content, flags=re.DOTALL)
            anchors_mk.append(None)
            return set(anchors_mk)

    def __repr__(self):
        return f"MarkdownNode(path='{self.path}', links={len(self.links)})"


class MarkdownGraph:
    def __init__(self, root_folder_path):
        self.nodes = {}
        self.root_folder_path = root_folder_path

    def add_node(self, path:str) -> MarkdownNode:
        if path not in self.nodes:
            self.nodes[path] = MarkdownNode(path, self.root_folder_path)
        return self.nodes[path]

    
    def add_link(self, from_path:str, to_path:str, to_anchor):
        if from_path in self.nodes and to_path in self.nodes:
            from_node = self.nodes[from_path]
            to_node = self.nodes[to_path]
            if to_anchor:
                if to_anchor in to_node.anchors:
                    from_node.add_link(to_node, anchor=to_anchor)
                else:
                    if STRICT:
                        raise ValueError(f"Anchor '{to_anchor}' not found in target node: '{to_path}'")
                    else:
                        logging.warning(f"Anchor '{to_anchor}' not found in target node: '{to_path}'")
                        from_node.add_link(to_node)
            else:
                from_node.add_link(to_node)
        else:
            raise ValueError(f"One or all of the nodes not found for linking: {from_path} -> {to_path}")

    def remove_node(self, path:str):
        if path in self.nodes:
            # 삭제할 node 찾기
            node_to_remove = self.nodes[path]
            # 모든 node들의 link에서 삭제할 node가 있는 링크 제거
            for node in self.nodes.values():
                _links = list(node.links)
                for link in _links:
                    if link[0] == node_to_remove:
                        node.remove_link(node_to_remove, link[1])
                del _links 
            del self.nodes[path]
        else:
            raise ValueError(f"Node not found: {path}")

    def update_link(self, old_path, new_path, old_anchor=None, new_anchor=None):
        if old_path in self.nodes and new_path in self.nodes:
            old_node = self.nodes[old_path]
            new_node = self.nodes[new_path]
            if old_anchor in old_node.anchors and new_anchor in new_node.anchors:
                for node in self.nodes.values():
                    if (old_node, old_anchor) in node.links:
                        node.remove_link(old_node, old_anchor)
                        node.add_link(new_node, new_anchor)
            else:
                raise ValueError(f"Anchor not found: {old_anchor} or {new_anchor}")
        else:
            raise ValueError(f"Node not found: {old_path} or {new_path}")

    def __repr__(self):
        return f"MarkdownGraph(nodes={len(self.nodes)})"

    def __str__(self):
        return f"MarkdownGraph(nodes={self.nodes})"


def build_markdown_graph(root_folder_path:str) -> MarkdownGraph:
    graph = MarkdownGraph(root_folder_path)
    file_paths = ray_tools.get_all_md_file_paths(root_folder_path)
    logging.info("Adding nodes to the graph")
    for file_path in file_paths:
        # Go through each markdown file, add them to the graph as nodes along with their named anchors
        relative_path = os.path.relpath(file_path, start=root_folder_path)
        graph.add_node(relative_path)
    logging.info("Finished Adding nodes to the graph")
    logging.info(f"Total number of markdown files: {len(file_paths)}")
    logging.info(f"Total nodes added: {len(graph.nodes)}\n")
    
    logging.info("Adding edges to the graph")
    
    for node in graph.nodes.values():
        full_path = node.full_path
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            modified_content = ray_tools.remove_code_blocks(content)
            markdown_links = re.findall(r'\[.*?\]\((.*?)\)', modified_content)
            for link in markdown_links:
                try:
                    parsed_link = ray_tools.parse_link(link)
                except ValueError as e:
                    if STRICT:
                        logging.error(f"Error in parsing: '{node.path}': {e}")
                        raise e
                    else:
                        logging.warning(f"Error in parsing: '{node.path}': {e}")
                        continue     
                if parsed_link['type'] == 'internal':
                    to_node_path = ray_tools.resolve_relative_link(node.path, parsed_link['link'])
                    try:
                        graph.add_link(node.path, to_node_path, parsed_link['anchor'] if 'anchor' in parsed_link else None)
                    except ValueError as e:
                        if STRICT:
                            logging.error(f"{e}")
                            raise e
                        else:
                            logging.warning(f"{e}")
                            continue
                elif parsed_link['type'] == 'same-page':
                    try:
                        graph.add_link(node.path, node.path, parsed_link['anchor'] if 'anchor' in parsed_link else None)
                    except ValueError as e:
                        if STRICT:
                            logging.error(f"{e}")
                            raise e
                        else:
                            logging.warning(f"{e}")
                            continue
                else:
                    logging.warning(f"Excluded Link from Graph: {parsed_link['link']}\nLink Type: {parsed_link['type']}")
                    continue
    
    return graph

def visualize_graph(graph: MarkdownGraph, output_path: str):
    nx_graph = nx.DiGraph()
    
    for node in graph.nodes.values():
        nx_graph.add_node(node.path)
    
    for node in graph.nodes.values():
        for link in node.links:
            nx_graph.add_edge(node.path, link[0].path)
    
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(nx_graph)
    nx.draw(nx_graph, pos, with_labels=False, node_size=1000, node_color='skyblue', font_size=5, font_weight='bold', arrows=True)
    plt.savefig(output_path)
    plt.show()
    
def main():
    root_folder_path = 'C:/Users/khy/Documents/workspace/devsite_mk/docs/ko'
    print("Building markdown graph...")
    markdown_graph = build_markdown_graph(root_folder_path)
    # print(markdown_graph)
    
    for node in markdown_graph.nodes.values():
        print(node)
        continue
    
    # Visualize and save the graph
    # print("Visualizing the graph...")
    # vis_output_path = os.path.dirname(__file__) + f'\\visualizations'
    # if not os.path.exists(vis_output_path):
    #     os.makedirs(vis_output_path)
    # vis_output_path += '\\graph_visualization.png'
    # ray_tools.save_results_to_file
    # visualize_graph(markdown_graph, vis_output_path)

if __name__ == '__main__':
    main()

