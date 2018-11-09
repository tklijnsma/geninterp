import os
import geninterp

class BaseBlock(object):
    """docstring for BaseBlock"""
    name = 'base'
    close_immediately = False
    closeable_by_EOF = False
    forbid_new_openings = False
    has_subinterpreter = False
    escape_char = None
    needs_associated_blocks = False

    def __init__(self, i_begin, text):
        super(BaseBlock, self).__init__()
        self.i_begin = i_begin
        self.text = text
        self.i_close = None
        self.association = []

    def __repr__(self):
        return '{0} ({1}:{2})'.format(self.name, self.i_begin, self.i_close)

    def advance_index_at_open(self):
        return 0

    def advance_index_at_close(self):
        return 0

    def get_text(self):
        return self.text[self.i_begin:self.i_close+1]

    def process(self, text=None):
        if text is None:
            r = self.get_text()
        else:
            r = text
        return r

    
class PlainBlock(BaseBlock):
    """docstring for PlainBlock"""
    name = 'plain'
    closeable_by_EOF = True


class OpenCloseTagBlock(BaseBlock):
    """docstring for OpenCloseTagBlock"""
    open_tag = ''
    close_tag = ''

    @classmethod
    def open(cls, text, i):
        if not(cls.escape_char is None):
            if text[i-1] == cls.escape_char: return False
        return text[i:i+len(cls.open_tag)].lower() == cls.open_tag.lower()
        
    def close(self, text, i):
        if not(self.escape_char is None):
            if text[i-1] == self.escape_char: return False
        return text[i:i+len(self.close_tag)].lower() == self.close_tag.lower()

    def advance_index_at_open(self):
        return len(self.open_tag)

    def advance_index_at_close(self):
        return len(self.close_tag)

    def process(self, text=None):
        return self.open_tag +  super(OpenCloseTagBlock, self).process(text) + self.close_tag


class OpenCloseTagBlockCaseSensitive(OpenCloseTagBlock):
    open_tag = ''
    close_tag = ''

    @classmethod
    def open(cls, text, i):
        return text[i:i+len(cls.open_tag)] == cls.open_tag

    def close(self, text, i):
        return text[i:i+len(self.close_tag)] == self.close_tag


class CommentBlock(OpenCloseTagBlock):
    """docstring for CommentBlock"""
    name = 'comment'
    closeable_by_EOF = True
    forbid_new_openings = True
    close_tag = '\n'

    def process(self, text=None):
        return ''
        

class InputBlock(OpenCloseTagBlock):
    """docstring for InputBlock"""
    name = 'input'
    open_tag = '\\input{'
    close_tag = '}'

    has_subinterpreter = True
    SubInterpreter = None

    has_base_path = False
    base_path = ''

    extension = None

    @classmethod
    def set_base_path(cls, base_path):
        cls.has_base_path = True
        cls.base_path = base_path

    @classmethod
    def set_subinterpreter(cls, SubInterpreter):
        cls.SubInterpreter = SubInterpreter

    def filestub_to_filename(self, stub):
        stub = stub.strip()
        if self.has_base_path:
            stub = os.path.join(self.base_path, stub)
        if not(self.extension is None):
            if not stub.endswith(self.extension):
                stub += self.extension
        return stub

    def run_subinterpreter(self, filestub):
        filename = self.filestub_to_filename(filestub)
        return self.SubInterpreter().interpret_file(filename)

    def process(self, text=None):
        if text is None:
            r = self.get_text()
        else:
            r = text
        return r
