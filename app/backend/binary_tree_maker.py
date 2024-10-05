#pip install schemdraw

from collections import deque
from dataclasses import dataclass
from typing import Generic, Type, TypeVar
import math
# For drawing flowchart
from schemdraw import flow
import schemdraw
import schemdraw.elements as elm

N = TypeVar('Node')

@dataclass
class PlotInfo:
    row: float
    col: float
    elem: schemdraw.flow.flow.Connect

class TreeNode:
    '''A node in a tree'''
    def __init__(self, id, data, color):
        self.id = id
        self.data = data
        self.color = color
        self.left = None
        self.right = None
        self.parent = None
        self.plot_info = None

    def next_sibling(self) -> N:
        '''Find the next sibling or the next node in the same level
        Returns:
            The sibling
        '''
        if self.parent is None:
            return None
        # I am the left child of my parent. My sibling is the right child of
        # my parent.
        if self.parent.left == self:
            return self.parent.right
        # I am the right child of my parent. Find the most immediate
        # ancestor who is the left child of his parent.
        cur, hop = self, 0
        while cur and cur.parent and cur != cur.parent.left:
            cur, hop = cur.parent, hop + 1
        # Navigate from the righ child of that parent for the same
        # distance that was traveled up the tree.
        if cur.parent:
            cur = cur.parent.right
            while hop > 0:
                cur, hop = cur.left, hop - 1
            return cur
        return None

class BinaryTree:
    def __init__(self):
        self.root = None
        self.step = 2
        self.node_map = {}

    def create_tree(self, nodes: list, edges: list) -> None:
        # Create all nodes and store in node_map
        for node in nodes:
            n = TreeNode(*node)
            self.node_map[n.id] = n

        # Link parent nodes to their children using edges
        for edge in edges:
            root, left, right = edge
            if left in self.node_map:
                self.node_map[root].left = self.node_map[left]
                self.node_map[left].parent = self.node_map[root]
            if right in self.node_map:
                self.node_map[root].right = self.node_map[right]
                self.node_map[right].parent = self.node_map[root]

        self.root = self.node_map[nodes[0][0]]  # Assuming the first node is the root

    def delete_empty_label_nodes(self, node):
        # Base case: if node is None, return None
        if node is None:
            return None

        # Recursively call for left and right children
        node.left = self.delete_empty_label_nodes(node.left)
        node.right = self.delete_empty_label_nodes(node.right)

        # If the node has an empty label, bypass it by returning its children
        if node.data.strip() == "":
            if node.left and node.right:
                # If both children exist, promote the left child and attach the right child
                self.attach_children(node.left, node.right)
                node.left.parent = node.parent
                return node.left
            elif node.left:
                # If only left child exists, return the left child
                node.left.parent = node.parent
                return node.left
            elif node.right:
                # If only right child exists, return the right child
                node.right.parent = node.parent
                return node.right
            else:
                # If no children, return None (delete node)
                return None
        return node

    def attach_children(self, left, right):
        # Attach the right child to the rightmost descendant of the left subtree
        cur = left
        while cur.right:
            cur = cur.right
        cur.right = right
        if right:
            right.parent = cur

    def get_tree_hierarchy(self) -> list[list[N]]:
        if self.root is None:
            return None
        hierarchy = []
        queue = deque([(self.root, 0)])
        while queue:
            level_size = len(queue)
            level = []
            for _ in range(level_size):
                node, depth = queue.popleft()
                while len(hierarchy) <= depth:
                    hierarchy.append([])
                hierarchy[depth].append(node)
                if node.left:
                    queue.append((node.left, depth + 1))
                if node.right:
                    queue.append((node.right, depth + 1))
        return hierarchy

    def draw(self, filename: str = None) -> None:
        if self.root is None:
            return None

        with schemdraw.Drawing(fontsize=8, unit=1) as drawing:
            hierarchy = self.get_tree_hierarchy()
            max_depth = len(hierarchy)

            def calculate_x_position(node, level, left, right, drawing):
                if node is None:
                    return

                # X and Y positions based on depth and horizontal span
                x = (left + right) / 2
                y = (max_depth - level - 1) * self.step  # Inverted y-axis

                # Node label and color
                label = str(node.data) if node.data is not None else ''
                elem = flow.Circle(r=0.5).label(label).at((x, y)).fill(node.color)
                drawing += elem
                node.plot_info = PlotInfo(y, x, elem)

                mid = (right - left) / 2
                calculate_x_position(node.left, level + 1, left, left + mid, drawing)
                calculate_x_position(node.right, level + 1, left + mid, right, drawing)

            # Calculate positions of nodes
            calculate_x_position(self.root, 0, 0, 2 ** (max_depth - 1), drawing)

            # Draw connections
            def draw_connections(node, drawing):
                if node is None:
                    return
                if node.left and node.left.plot_info:
                    drawing += elm.Arrow().at(node.plot_info.elem.S).to(node.left.plot_info.elem.N)
                if node.right and node.right.plot_info:
                    drawing += elm.Arrow().at(node.plot_info.elem.S).to(node.right.plot_info.elem.N)
                draw_connections(node.left, drawing)
                draw_connections(node.right, drawing)

            draw_connections(self.root, drawing)

            if filename is not None:
                drawing.save(filename, dpi=300)


# Sample usage
adj_list_data = [
    {
        "description": "primera_solucion_factible",
        "filename": "primera_solucion_factible.jpg",
        "data": {
            'root': 0,
            'nodes': [
                (0, 'root', "white"), (1, 'x_1=0\nz=3.48', "white"),
                (2, 'x_1=1\nz=3.52', "white"), (3, 'x_2=0\nz=3.48', "white"),
                (4, 'x_2=1\nz=3.3', "white"), (5, 'x_2=0\nz=3.52', "white"),
                (6, 'x_2=1\nz=3.2', "white"), (7, 'x_3=0\nz=2.2', "white"),
                (8, 'x_3=1\nz=3.45', "white"), (11, 'x_3=0\nz=3.2', "white"),
                (12, 'x_3=1\nz=3.4', "green"), (17, 'x_4=0\nz=3', "white"),
                (18, 'x_4=1\nz=3.45', "white"), (37, 'x_5=0\nz=2.4', "white"),
                (38, 'no sol.', "black"),
            ],
            'edges': [
                (0, 1, 2), (1, 3, 4), (2, 5, 6),
                (3, 7, 8), (5, 11, 12), (8, 17, 18),
                (18, 37, 38),
            ]
        }
    }
]

for adj_list in adj_list_data:
    tree = BinaryTree()
    tree.create_tree(adj_list['data']['nodes'], adj_list['data']['edges'])

    # Remove nodes with empty labels
    tree.root = tree.delete_empty_label_nodes(tree.root)

    # Draw the cleaned-up tree
    tree.draw(f"tree_diagram_{adj_list['description']}.png")