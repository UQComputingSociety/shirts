import os
from mako.lookup import TemplateLookup

file_root = os.path.dirname(__file__)
lookup = TemplateLookup([
    os.path.join(file_root, "views"), os.path.join(file_root, "emails")
], input_encoding='utf-8')