
from geninterp import DocTree
from geninterp.blocks import *

import logging


class Interpreter(object):
    """docstring for Interpreter"""

    blocks = []

    def __init__(self, blocks=None):
        super(Interpreter, self).__init__()
        if not(blocks is None):
            self.blocks += blocks

        # Set default subinterpreters to the same as this one
        for block in self.blocks:
            if block.has_subinterpreter and block.SubInterpreter is None:
                block.set_subinterpreter(self.__class__)

        self.filename = None

    def interpret_file(self, filename):
        self.filename = filename
        with open(filename, 'r') as fp:
            text = fp.read()
        return self.interpret(text)

    def set_base_file(self, filename):
        """
        When dealing with relative paths in input files, it's easier
        to tell explicitily relative to which file the paths are
        """
        base_path_for_input = os.path.abspath(os.path.dirname(filename))
        for block in self.blocks:
            if issubclass(block, InputBlock):
                block.set_base_path(base_path_for_input)

    def interpret(self, text):
        N = len(text)
        tree = DocTree(text)

        # A continually replaced block containing only plain text
        plain = PlainBlock(i_begin=0, text=text)

        i = 0
        while i < N:
            active_node = tree.active_node()
            forbid_new_openings = tree.active_node().forbid_new_openings() if tree.active_node() else False

            # First try to open new blocks
            if not(forbid_new_openings):
                block_opened = False
                for Block in self.blocks:
                    if Block.open(text, i):
                        if i - plain.i_begin > 0:
                            # Push the existing PlainBlock as a child of the last node
                            tree.push(plain)
                            tree.close(i-1) # Close immediately; plain text has no children
                        tree.push(Block(i_begin=i, text=text))
                        i += tree.active_node().block.advance_index_at_open() # Advance by a bit if necessary, to skip over e.g. an opening tag
                        if tree.active_node().block.close_immediately: # Some blocks do not wait for a closing tag
                            if tree.active_node().has_subinterpreter(): tree.active_node().run_subinterpreter()
                            tree.close(i) # Pop active node off the stack and record closing index
                            i += 1
                        plain = PlainBlock(i_begin=i, text=text) # Open up a fresh plain text block
                        block_opened = True
                        break
                if block_opened: continue

            # Not opening a new tag, so let's see if we can close an open block (excluding the root)
            if tree.active_node() and tree.active_node().block.close(text, i):
                if i - plain.i_begin > 0:
                    # Push the existing PlainBlock as a child of the last node
                    tree.push(plain)
                    tree.close(i-1) # Close immediately; plain text has no children

                if tree.active_node().has_subinterpreter(): tree.active_node().run_subinterpreter()

                n_advance_index_at_close = tree.active_node().block.advance_index_at_close()
                tree.close(i) # Pop active node off the stack and record closing index
                i += n_advance_index_at_close
                plain = PlainBlock(i_begin=i, text=text) # Open up a fresh plain text block
                continue

            # No block opened or closed, so this char is plain text
            # Do nothing
            i += 1

        # Push the remaining text if not zero length
        if N-1 - plain.i_begin > 0:
            tree.push(plain)
            tree.close(N-1) # Close immediately; plain text has no children

        # Close remaining open blocks if any
        for node in tree.stack[1:]:
            if node.block.closeable_by_EOF:
                node.block.i_close = N-1
            else:
                logging.error('Encountered error; tree so far:')
                logging.error(tree.render_structure())
                raise ValueError('{0} is open, but is not allowed to closed by EOF'.format(node))

        return tree

