from unittest import TestCase

import geninterp
import logging
import os

class TestInterpreter(TestCase):

    def setUp(self):

        class BracketBlock(geninterp.blocks.OpenCloseTagBlock):
            name = 'bracket'
            open_tag = '{'
            close_tag = '}'

        class CommentBlock(geninterp.blocks.CommentBlock):
            name = 'comment'
            open_tag = '%'
            escape_char = '\\'

        class CiteBlock(geninterp.blocks.OpenCloseTagBlock):
            name = 'cite'
            open_tag = '\\cite{'
            close_tag = '}'

        class InputBlock(geninterp.blocks.InputBlock):
            name = 'input'
            open_tag = '\\input{'
            close_tag = '}'
            extension = '.tex'

        self.interpreter = geninterp.Interpreter(blocks=[BracketBlock, CommentBlock, CiteBlock, InputBlock])


    def test_nothing(self):
        tree = self.interpreter.interpret('')
        self.assertEqual(tree.parse(), '')

    def test_onlyplain(self):
        tree = self.interpreter.interpret('aaaa')
        self.assertEqual(tree.parse(), 'aaaa')

    def test_comment(self):
        tree = self.interpreter.interpret('aaaa%bbbb')
        self.assertEqual(tree.parse(), 'aaaa')
        tree = self.interpreter.interpret('aaaa%bbbb\ncccc')
        self.assertEqual(tree.parse(), 'aaaacccc')

    def test_escaped_comment(self):
        tree = self.interpreter.interpret('aaaa\\%bbbb')
        self.assertEqual(tree.parse(), 'aaaa\\%bbbb')

    def test_cite(self):
        tree = self.interpreter.interpret('aaaa\cite{bbbb}')
        self.assertEqual(tree.parse(), 'aaaa\cite{bbbb}')
        tree = self.interpreter.interpret('aaaa\cite{bb%cc\nbb}')
        self.assertEqual(tree.parse(), 'aaaa\cite{bbbb}')


class TestInterpreterWithInput(TestInterpreter):

    tmp_tex_input_file = 'test_inputtable.tex'

    def setUp(self):
        super(TestInterpreterWithInput, self).setUp()
        with open(self.tmp_tex_input_file, 'w') as fp:
            fp.write('aa{bb}cc')

    def tearDown(self):
        os.remove(self.tmp_tex_input_file)

    def test_input(self):
        tree = self.interpreter.interpret('11\\input{{{0}}}22'.format(self.tmp_tex_input_file))
        self.assertEqual(tree.parse(), '11aa{bb}cc22')

