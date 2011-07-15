
__doc__ = """Contains classes for sitemap tree."""

class SitemapTreeElement(object):
    """Base class for sitemap elements"""
    
    def __init__(self, depth = 0, parent = None):
        """Initializes sitemap element base properties.
        
        depth --  number of clicks we need to do in order to reach this element 
                  from a websitesite homepage; actualy, it is a depth of an 
                  element in a sitemap tree (by default is 0)
        parent -- sitemap element which is the parent of a current element 
                  (by default is None)
                  
        """
        
        # Check a type of 'depth' parametr
        if not isinstance(depth, (int, long)):
            raise TypeError('int or long type expected')
        self._depth = depth

        # Check a type of 'parent' parametr
        if parent and not isinstance(parent, SitemapTreeElement):
            raise TypeError('SitemapTreeElement type expected')
        self._parent = parent

        # self._children contains a list of sitemap element children.
        # Initialize it with an empty list.
        self._children = []
        
    @property
    def depth(self):
        """Returns depth of a sitemap element."""
        
        return self._depth
        
    @property
    def parent(self):
        """Returns parent of a sitemap element."""
        
        return self._parent
    
    @property    
    def children(self):
        """Returns a list containing sitemap element children."""
        
        return self._children

    @depth.setter
    def depth(self, new_depth):
        """Sets depth of a sitemap element."""
        
        # Check a type of 'new_depth' parametr        
        if not isinstance(new_depth, (int, long)):
            raise TypeError('int or long type expected')
        self._depth = new_depth

    @parent.setter
    def parent(self, new_parent):
        """Sets parent of a sitemap element."""

        # Check a type of 'new_parent' parametr
        if not isinstance(new_parent, SitemapTreeElement):
            raise TypeError('SitemapTreeElement type expected')
        self._parent = new_parent
    
    def append_child(self, child):
        """Appends a child element to a sitemap element.
        
        child -- corresponding SitemapTreeElement class instance
        
        """
        
        # Check a type of 'child' parametr
        if not isinstance(self, SitemapTreeElement):
            raise TypeError('SiteMapTreeElement type expected')
        self._children.append(child)
        
        
class HeadlineElement(SitemapTreeElement):
    """Class for sitemap elements that contains headlines.
    Such element may contain a headline of a references group and so on."""
    
    def __init__(self, headline, depth = 0, parent = None):
        """Initializes sitemap headline element properties.

        headline --  hadline of an element
        depth --     number of clicks we need to do in order to reach this element 
                     from a websitesite homepage; actualy, it is a depth of an 
                     element in a sitemap tree (by default is 0)
        parent --    sitemap element which is the parent of a current element 
                     (by default is None)
        
        """
        
        SitemapTreeElement.__init__(self, depth, parent)

        # Check a type of 'headline' parametr
        if not isinstance(headline, basestring):
            raise TypeError('string type expected')
        self._headline = headline
        
    @property
    def headline(self):
        """Returns headline of a headline element"""
        
        return self._headline
    
    @headline.setter
    def headline(self, new_headline):
        """Sets headline of a headline element"""

        # Check a type of 'new_headline' parametr
        if not isinstance(new_headline, basestring):
            raise TypeError('string type expected')
        self._headline = new_headline

        
class TextReferenceElement(SitemapTreeElement):
    """Class for sitemap elements that contains text references."""
    
    def __init__(self, reference, title, depth = 0, parent = None):
        """Initializes sitemap text reference element properties.
        
        reference -- corresponding URL
        title --     title of a text reference
        depth --     number of clicks we need to do in order to reach this element 
                     from a websitesite homepage; actualy, it is a depth of an 
                     element in a sitemap tree (by default is 0)
        parent --    sitemap element which is the parent of a current element
                     (by default is None)
                  
        """

        SitemapTreeElement.__init__(self, depth, parent)

        # Check a type of 'reference' parametr
        if not isinstance(reference, basestring):
            raise TypeError('string type expected')
        self._reference = reference

        # Check a type of 'title' parametr
        if not isinstance(title, basestring):
            raise TypeError('string type expected')
        self._title = title
       
    @property
    def reference(self):
        """Returns reference of a text reference element."""
        
        return self._reference
        
    @property
    def title(self):
        """Returns title of a text reference element."""

        return self._title

    @reference.setter
    def reference(self, new_reference):
        """Sets reference of a text reference element."""

        # Check a type of 'new_reference' parametr
        if not isinstance(new_reference, basestring):
            raise TypeError('string type expected')
        self._reference = new_reference

    @title.setter
    def title(self, new_title):
        """Sets title of a text reference element."""

        # Check a type of 'new_title' parametr
        if not isinstance(new_title, basestring):
            raise TypeError('string type expected')
        self._title = new_title
