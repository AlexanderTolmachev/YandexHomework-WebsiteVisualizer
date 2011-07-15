from lxml import etree

__doc__ = """
Contains website HTML pages parser and auxiliary classes. 
Uses third-party lxml library for parsing HTML documents.
"""

class ReferenceParsingInfo(object):
    """Base class for parsing information about references retrieved 
    from a site page. Reference may be not just a text reference, it also
    for example may be an image reference. But at the current time we will 
    only deal with text references.
    
    """
    
    def __init__(self, reference):
        """Initializes reference value.
        
        reference -- corresponding URL, actually 'href' attribute value of
                     HTML 'a' tag
        
        """

        # Check a type of 'reference' parametr
        if not isinstance(reference, basestring):
            raise TypeError('string type expected')
        self._reference = reference
        
    @property
    def reference(self):
        """Returns reference value."""
        
        return self._reference
    
    @reference.setter
    def reference(self, new_reference):
        """Sets reference value."""
        
        # Check a type of 'new_reference' parametr
        if not isinstance(new_reference, basestring):
            raise TypeError('string type expected')
        self._reference = new_reference
        
    
class TextReferenceParsingInfo(ReferenceParsingInfo):
    """Class for parsing information about text references retrieved 
    from a site page. At the current time we only deal with text references.
    
    """
    
    def __init__(self, reference, title):
        """Initializes text reference parsing information.
        
        reference -- corresponding URL, actually 'href' attribute value of
                     HTML 'a' tag
        title --     title of a text reference
        
        """

        ReferenceParsingInfo.__init__(self, reference)

        # Check a type of 'title' parametr
        if not isinstance(title, basestring):
            raise TypeError('string type expected')
        self._title = title

    @property
    def title(self):
        """Returns text reference title."""
        
        return self._title
    
    @title.setter
    def title(self, new_title):
        """Sets text reference title."""

        # Check a type of 'new_title' parametr
        if not isinstance(new_title, basestring):
            raise TypeError('string type expected')
        self._title = new_title
        

class ReferencesGroupParsingInfo(object):
    """This class is intended to contain parsing information about a group
    of references, such as group headline and parsing information about
    references theirselfs. References group is allowed to have no headline.
    
    """
    
    def __init__(self, headline = ''):
        """Initializes references group parsing information.
        
        headline -- headline of a group of references
        
        """
        
        # Check a type of 'headline' parametr
        if not isinstance(headline, basestring):
            raise TypeError('string type expected')
        self._headline = headline
        
        # self._references contains a list of ReferenceParsingInfo class 
        # instances corresponding to references in the group.
        # Initialize it with an empty list.
        self._refrences = []
        
    @property
    def headline(self):
        """Returns references group headline."""
        
        return self._headline
                    
    @property
    def references(self):
        """Returns a list containing ReferenceParsingInfo class instances 
        corresponding to references in the group.
        
        """
        
        return self._refrences
    
    @headline.setter
    def headline(self, new_headline):
        """Sets references group headline."""

        # Check a type of 'new_headline' parametr
        if not isinstance(new_headline, basestring):
            raise TypeError('string type expected')
        self._headline = new_headline

    def add_reference(self, reference_info):
        """Adds parsing information about reference in the group.

        reference info -- corresponding ReferenceParsingInfo class instance
        
        """

        # Check a type of 'reference_info' parametr
        if not isinstance(reference_info, ReferenceParsingInfo):
            raise TypeError('ReferenceParsingInfo type expected')
        self._refrences.append(reference_info)
    
    
class PageParsingInfo(object):
    """This class is intended to contain parsing information about parsed 
    website page. At the current time this information consists of page title
    and parsing information about groups of references retrieved from this page.
    
    """
    
    def __init__(self, title):
        """Initializes page parsing information.

        title -- website page title, actually text of 'title' tag of 
                 HTML document
                 
        """
        
        # Check a type of 'title' parametr
        if not isinstance(title, basestring):
            raise TypeError('string type expected')
        self._title = title
        
        # self._references_groups contains a list of ReferencesGroupParsingInfo 
        # class instances corresponding to page references groups
        # Initialize it with an empty list.
        self._references_groups = []
        
    @property
    def title(self):
        """Returns page title."""
        
        return self._title
            
    @property
    def references_groups(self):
        """Returns a list of ReferencesGroupParsingInfo class instances 
        corresponding to page references groups.
        
        """
        
        return self._references_groups
    
    @title.setter
    def title(self, new_title):
        """Sets page title."""
        
        # Check a type of 'new_title' parametr
        if not isinstance(new_title, basestring):
            raise TypeError('string type expected')
        self._title = new_title

    def add_references_group(self, references_group):
        """Adds parsing information about page references group.
        
        references_group -- corresponding ReferencesGroupParsingInfo 
                            class instance
                            
        """
        
        if not isinstance(references_group, ReferencesGroupParsingInfo):
            raise TypeError('ReferencesGroupParsingInfo type expected')
        self._references_groups.append(references_group)

    def find_references_group_by_headline(self, headline):
        """Looks trough all page references groups in order to find
        group of references corresponding to headline. 

        headline -- headline of references group that should be found. 
                    Note that page may contain several groups of references 
                    with no headline. So, if you pass '' as headline parametr,
                    you will get only the first references group without 
                    headline.
        
        Returns corresponding ReferencesGroupParsingInfo class instance if 
        group was found or None otherwise.
        
        """
        
        for references_group in self._references_groups:
            if references_group.headline == headline:
                return references_group
            
        return None
 
    
class SitePageParseError(Exception):
    """Class for site page parser errors. Also contanins a lxml library
    etree.LxmlError exception for further error information."""
    
    def __init__(self, lxml_error):
        self._lxml_error = lxml_error
        
    def __str__(self):
        return 'Error while parsing site page: ' + str(self._lxml_error)

    
class SitePageParser(object):
    """Website page parser class. Page parser is intended to retrieve title
    and all references groups from a HTML document.
    
    """

    def _find_preceding_headline_tag(self, element):
        """Looks through preceding siblings of a given element, then through 
        element parent and preceding siblings of a parent and so on (just like
        upstairs walking) till the top of a pgae is reached in order to find 
        headline tag which precedes given element.
        
        element -- lxml.Element class instance corresponding to a tag in 
                   HTML document.
         
        Retruns lxml.Element class instance corresponding to preceding headline
        tag if appropriate tag was found and None otherwise.
        
        """
        
        # Define which tags are appropriate
        headline_tags = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')
        # Start search from the given element
        preceding_element = element
        # Search until the top of the page is reached or appropriate 
        # tag was found
        while preceding_element is not None:
            if preceding_element.tag in headline_tags:
                return preceding_element
            for preceding_sibling in preceding_element.itersiblings(preceding=True):

                if preceding_sibling.tag in headline_tags:
                    return preceding_sibling
                preceding_element = preceding_sibling
            preceding_element = preceding_element.getparent()

        # If no approptiate tag was found return None
        return None
    
    def parse_site_page(self, page_text):
        """Parses given website HTML page in order to retrieve page title and
        all page references groups that are contained in 'ul' or 'ol' HTML tags.

        page_text -- string containing HTML document
        
        Returns PageParsingInfo class instance which contains parsing information
        about parsed website page. Raises SitePageParseError exception in case of
        parse error.
        
        """
        
        # Try to feed HTML page to lxml HTML parser
        try:
            lxml_tree = etree.HTML(page_text)
        except etree.LxmlError, lxml_error:
            raise SitePageParseError(lxml_error)
 
        # Retrieve page title
        page_title_text = lxml_tree.xpath('//title/text()')
        if page_title_text:
            page_title = page_title_text[0].strip()
        else:
            page_title = ''
            
        page_parsing_info = PageParsingInfo(page_title)
        
        # Set of references groups headlines that were already retrieved
        # from page
        page_headlines = set()

        # Retrieve all lists ('ul' and 'ol' HTML tags) from page
        page_lists = lxml_tree.xpath('//ul | //ol')
 
        # Retrieve groups of references
        for page_list in page_lists:
            # Look for references in current list
            reference_tags = page_list.xpath('.//li//a[@href]')
            if reference_tags:
                # Look for headline for new reference group
                preceding_headline_tag = \
                        self._find_preceding_headline_tag(page_list)
                if preceding_headline_tag is not None:
                    preceding_headline_text = \
                            preceding_headline_tag.xpath('.//text()')
                    if preceding_headline_text:
                        preceding_headline = preceding_headline_text[0].strip()
                    else:
                        preceding_headline = ''
                else:
                    preceding_headline = ''

                # If headline was found and it is one of the titles of 
                # references groups that were already retrieved from page
                # we should not create new group of references, we should
                # add new refernces to a group corresponding to this title.
                # In opposite situation we should create a new group 
                # of references.
                if not preceding_headline or \
                        preceding_headline not in page_headlines:
                    # Create a new references group and set as current
                    references_group_headline = preceding_headline
                    new_references_group = \
                            ReferencesGroupParsingInfo(references_group_headline)
                    page_parsing_info.add_references_group(new_references_group)
                    current_references_group = new_references_group
                    page_headlines.add(preceding_headline)
                else: 
                    # Find references group corresponding to headline and 
                    # set it as current
                    current_references_group = \
                            page_parsing_info.find_references_group_by_headline(
                                    preceding_headline)
 
                # Add new references to the current group of references
                for reference_tag in reference_tags:
                    # Extract reference parsing info
                    reference = reference_tag.attrib['href']
                    reference_tag_text = reference_tag.xpath('.//text()')
                    # Because at the current time we only deal with 
                    # text references it may happen that reference
                    # has no title
                    if reference_tag_text:
                        reference_title = reference_tag_text[0].strip()
                    else:
                        reference_title = ''
                    # Add new reference to current group of references
                    reference_parsing_info = TextReferenceParsingInfo(reference, 
                                              reference_title)
                    current_references_group.add_reference(reference_parsing_info)
            
        return page_parsing_info
    
                    