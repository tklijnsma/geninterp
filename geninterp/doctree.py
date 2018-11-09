# -*- coding: utf-8 -*-

import geninterp
import logging

class RenderTree(object):
    def __init__(self, root):
        self.root = root

def iter_dfs_preorder(node, depth=0):
    node.iter_depth = depth
    yield node
    for child in node.children:
        for c in iter_dfs_preorder(child, depth=depth+1):
            yield c

def iter_dfs_inorder(node, depth=0):
    node.iter_depth = depth
    for child in node.children:
        for c in iter_dfs_inorder(child, depth=depth+1):
            yield c
    yield node


class Node(object):
    def __init__(self, parent=None):
        super(Node, self).__init__()
        self.children = []
        self.parent = parent
        if parent:
            parent.children.append(self)

    def is_childless(self):
        return len(self.children) == 0

    def has_children(self):
        return len(self.children) > 0

    def render_structure(self, print_method='__repr__', prepend_space=''):
        structure = [ node for node in iter_dfs_preorder(self) ]

        attempt_straight_lines = True
        if len(structure) > 250:
            logging.warning('Found {0} nodes; omitting straight lines'.format(len(structure)))
            attempt_straight_lines = False

        space  = '    '
        tspace = '│   ' 
        ctab   = '└── '
        xtab   = '├── '

        output_str = []

        for inode, node in enumerate(structure):
            if inode == 0:
                output_str.append(getattr(node, print_method)()) # is the root
            elif node == structure[-1]:
                output_str.append((node.iter_depth-1)*space + ctab + getattr(node, print_method)()) # Is the final leaf
            else:
                if attempt_straight_lines:
                    # Determine where to put straight lines
                    preceding_nodes = [ n for n in structure[:inode] if n.iter_depth <= node.iter_depth ]
                    succeeding_nodes = [ n for n in structure[inode+1:] if n.iter_depth <= node.iter_depth ]
                    draw_straight_line_at_depths = []
                    for succeeding_node in succeeding_nodes:
                        for preceding_node in preceding_nodes:
                            if succeeding_node in preceding_node.children:
                                draw_straight_line_at_depths.append(succeeding_node.iter_depth)
                                break

                # Compile the indent up to the second-to-last one
                indent = ''
                for i in xrange(1,node.iter_depth):
                    if attempt_straight_lines and i in draw_straight_line_at_depths:
                        indent += tspace
                    else:
                        indent += space

                # Compile the last indent (T-shape or corner depending on whether succeeding nodes connect to the same parent)
                if  attempt_straight_lines and node.iter_depth in draw_straight_line_at_depths:
                    indent += xtab
                else:
                    indent += ctab

                output_str.append(indent + getattr(node, print_method)())

        return prepend_space + (prepend_space+'\n').join(output_str)


class BlockNode(Node):
    """docstring for BlockNode"""
    def __init__(self, parent=None, block=None, text=None):
        super(BlockNode, self).__init__(parent=parent)
        self.block = block
        if not block is None:
            self.block.text = text
        self.associated_nodes = []

    def __repr__(self):
        text = ''
        if hasattr(self.block, 'get_text'):
            text = ' "' + self.block.get_text().replace('\n', '\\n') + '"'
        r = '<Node {0}{1}>'.format(self.block, text)
        return r

    def parse(self):
        if self.is_childless():
            return self.block.process()
        else:
            return self.block.process(
                ''.join([child.parse() for child in self.children])
                )

    def run_subinterpreter(self):
        parsed_included_text = self.parse()
        subtree = self.block.run_subinterpreter(parsed_included_text)
        self.children = subtree.root.children

    def has_subinterpreter(self):
        return self.block.has_subinterpreter

    def forbid_new_openings(self):
        return self.block.forbid_new_openings


class RootNode(BlockNode):
    """docstring for RootNode"""
    def __init__(self):
        super(RootNode, self).__init__()
        
    def __repr__(self):
        return '<Root>'

    def parse(self):
        return ''.join([child.parse() for child in self.children])


class DocTree(object):
    """docstring for DocTree"""
    def __init__(self, text):
        super(DocTree, self).__init__()
        self.root = RootNode()
        self.stack = [ self.root ]
        self.text = text

    def active_node(self):
        if len(self.stack) > 1:
            return self.stack[-1]
        else:
            return None

    def push(self, block):
        node = BlockNode(parent=self.stack[-1], block=block, text=self.text)
        self.stack.append(node)

    def close(self, i_close=None):
        closed_node = self.stack.pop()
        closed_node.block.i_close = i_close

    def render_structure(self):
        return self.root.render_structure()

    def parse(self):
        return self.root.parse()

    def gen_blocks_by_name(self, name):
        for node in iter_dfs_preorder(self.root):
            if node.block is None: continue
            if node.block.name == name:
                yield node



