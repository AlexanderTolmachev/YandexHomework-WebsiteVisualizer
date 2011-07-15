import codecs

import markup

from sitemap_tree import TextReferenceElement, HeadlineElement

__doc__ = """
Contains sitemap html writer.
Uses third-party markup library to produce HTML documents and
sitemap_tree module to process given sitemap tree elements.
"""

class SitemapHtmlWriterError(Exception):
    """Class for errors of sitemap html writer. Contains exception of
    murkup library markup.MarkupError for further error information.
    
    """
    
    def __init__(self, markup_exception):
        self._markup_exception = markup_exception
        
    def __str__(self):
        return 'Error while writing sitemap to html: ' + \
                str(self._markup_exception)

class SitemapHtmlWriter:
    """Sitemap html writer class."""
    
    # HTML head parametrs
    HTML_PAGE_CHARSET = 'utf-8'
    HTML_PAGE_ENCODING = 'utf-8'
    CSS_FILE_NAME = 'src/sitemap.css'
    SCRIPT_FILE_NAME = 'src/sitemap.js'
    SCRIPT_TYPE = 'javascript'   

    # Classes of html elements containing sitemap elements
    # We well use them to set styles for the sitemap the map with help of CSS
    SITEMAP_TITLE_CLASS = 'SitemapTitle'
    SITEMAP_TREE_CLASS = 'SitemapTree'
    SITEMAP_NODE_CONTAINER_CLASS = 'NodeContainer'
    SITEMAP_ROOT_CLASS = 'SitemapNode Root ExpandClosed'
    SITEMAP_NODE_CLASS = 'SitemapNode ExpandClosed'
    SITEMAP_LEAF_CLASS = 'SitemapNode ExpandLeaf'
    SITEMAP_LAST_CHILD_CLASS = 'LastChild'
    SITEMAP_NODE_EXPAND_CLASS = 'Expand'
    SITEMAP_NODE_CONTENT_CLASS = 'NodeContent'
    SITEMAP_TEXT_REFERENCE_CLASS = 'TextReference'
    SITEMAP_HEADLINE_CLASS = 'Headline'
    
    def __init__(self, sitemap_tree, output_file_name):
        """Initializes sitemap html writer.
        
        sitemap_tree --     sitemap tree which is intended to be writen
                            to html file
        output_file_name -- name of an output html file
        
        """
        
        self._sitemap_tree = sitemap_tree
        self._output_file_name = output_file_name

        # Create an empty html page
        self._html_page = markup.page()
    
    def write_sitemap_tree_to_html(self):        
        """Writes sitemap to html file."""
        
        # Initialize page head tags according to markup specific
        page_title = self._sitemap_tree.title + ': Sitemap'
        script = {self.SCRIPT_FILE_NAME: self.SCRIPT_TYPE}
        # Write page head
        self._html_page.init(title = page_title, css = self.CSS_FILE_NAME, 
                charset = self.HTML_PAGE_CHARSET, 
                encoding = self.HTML_PAGE_ENCODING,
                script = script)

        # Write sitemap title
        self._html_page.div.open(class_ = self.SITEMAP_TITLE_CLASS)
        self._html_page.h1.open()
        self._html_page.add(self._sitemap_tree.title)
        self._html_page.br()
        self._html_page.add('Sitemap')
        self._html_page.h1.close()
        self._html_page.div.close()
 
        sitemap_tree_root = self._sitemap_tree

        # Try to write sitemap to html
        try:
            self._html_page.div.open(class_ = self.SITEMAP_TREE_CLASS, 
                                     onclick = 'tree_toggle(arguments[0])')
            self._write_sitemap_tree_element_to_html(sitemap_tree_root, None)
            self._html_page.div.close()
        except markup.MarkupError, markup_error:
            raise SitemapHtmlWriterError(markup_error)
        
        # Write created page to output file
        output_file = codecs.open(self._output_file_name, 'wb', 'utf-8')
        output_file.write(self._html_page())
        output_file.close()
        

    def _write_sitemap_tree_element_to_html(self, tree_element, 
                                            tree_element_parent):
        """Writes sitemap element and all its descendants to html.

        tree_element --        sitemap element, which is intended to be written
                               to html
        tree_element_parent -- parent of this element
        
        Recursively calls itself in order to write all tree element children 
        to html.
        
        """
        
        # Open a tag which is a container for sitemap element and 
        # all its descendants
        self._html_page.ul.open(class_ = self.SITEMAP_NODE_CONTAINER_CLASS)
 
        # Set a class of a sitemap element
        if tree_element == self._sitemap_tree:
            li_class = self.SITEMAP_ROOT_CLASS
        else:
            if not tree_element.children:
                li_class = self.SITEMAP_LEAF_CLASS
            else:
                li_class = self.SITEMAP_NODE_CLASS
            if tree_element == tree_element_parent.children[-1]:
                li_class += ' ' + self.SITEMAP_LAST_CHILD_CLASS
                        
        # Open tag which will contain sitemap element
        self._html_page.li.open(class_ = li_class)
        # Put list expand tag
        self._html_page.div.open(class_ = self.SITEMAP_NODE_EXPAND_CLASS)
        self._html_page.div.close()
        
        # Write sitemap element to html according to ist type
        if isinstance(tree_element, TextReferenceElement):
            # Set a class of tag which will contain text teference element
            text_reference_depth = tree_element.depth
            div_class = self.SITEMAP_NODE_CONTENT_CLASS + ' ' + \
                    self.SITEMAP_TEXT_REFERENCE_CLASS + \
                    '_level_%d' % text_reference_depth
            # Write text reference element to html
            self._html_page.div.open(class_ = div_class)
            reference = tree_element.reference
            reference_title = tree_element.title
            self._html_page.a(reference_title, href = reference)
            self._html_page.div.close()
        elif isinstance(tree_element, HeadlineElement):
            # Set a class of tag which will contain headline element
            headline_depth = tree_element.depth
            hedline_text = tree_element.headline
            div_class = self.SITEMAP_NODE_CONTENT_CLASS + ' ' + \
                    self.SITEMAP_HEADLINE_CLASS + \
                    '_level_%d' % headline_depth
            # Write text headline element to html
            self._html_page.div.open(class_ = div_class)
            self._html_page.add(hedline_text)
            self._html_page.div.close()
            
        # Write sitemap element children to html
        for tree_element_child in tree_element.children:
            self._write_sitemap_tree_element_to_html(tree_element_child, 
                    tree_element)
        
        # Close tag which contains sitemap element
        self._html_page.li.close()
        # Close a tag which is a container for sitemap element and
        # all its descendants
        self._html_page.ul.close()
            
        
