import urllib2        # For downloading resourses from Internet
import urlparse       # For operations with URL stings
import socket         # For using socket.error exception
import httplib        # For using httplib.InvalidURL, httplib.HTTPException
                      # and httplib.NotConnected exceptions
import exceptions     # For using ValueError and IOError exceptions
import robotparser    # For parsing robots.txt files
import time           # For using time.sleep() function
import random         # For using random numbers generator
import logging        # For logging

from sitemap_tree import SitemapTreeElement, HeadlineElement, \
                         TextReferenceElement
from site_page_parser import SitePageParser, SitePageParseError


__doc__ = """
Contains site spider and auxiliary classes.
Uses site_page_parser module to parse website pages and
sitemap_tree module to build sitemap tree.
"""

__all__ = ["SiteSpider"]

class ReferenceCrawlingInfo(object):
    """Base class for clawling information about reference. Reference may be 
    not just a text reference, it also for example may be an image reference. 
    But at the current time we will only deal with text references.
    
    """
    
    def __init__(self, reference, depth, parent = None):
        """Initializes reference crawlong info base properties.
        
        reference -- corresponding URL
        depth --     crawling depth of reference - number of clicks we need 
                     to do in order to reach a resourse corresponding to this 
                     reference from a websitesite homepage
        parent --    sitemap element which is intended to be a parent of a 
                     sitemap element corresponding to this reference 
                     (by default is None)
                    
        """
        
        # Check a type of 'reference' parametr        
        if not isinstance(reference, basestring):
            raise TypeError('string type expected')
        self._reference = reference

        # Check a type of 'depth' parametr        
        if not isinstance(depth, (int, long)):
            raise TypeError('int or long type expected')        
        self._depth = depth

        # Check a type of 'parent' parametr        
        if parent and not isinstance(parent, SitemapTreeElement):
            raise TypeError('SitemapTreeElement type expected')
        self._parent = parent
        
    @property
    def reference(self):
        """Returns reference value."""

        return self._reference
        
    @property
    def depth(self):
        """Returns reference crawling depth."""

        return self._depth
    
    @property
    def parent(self):
        """Returns reference sitemap parent element."""

        return self._parent
    
    @reference.setter
    def reference(self, new_reference):
        """Sets reference value."""

        # Check a type of 'new_reference' parametr        
        if not isinstance(new_reference, basestring):
            raise TypeError('string type expected')
        self._reference = new_reference
        
    @depth.setter
    def depth(self, new_depth):
        """Sets reference crawling depth."""

        # Check a type of 'new_depth' parametr        
        if not isinstance(new_depth, (int, long)):
            raise TypeError('int or long type expected')        
        self._depth = new_depth
        
    @parent.setter
    def parent(self, new_parent):
        """Sets reference sitemap parent element."""

        # Check a type of 'new_parent' parametr        
        if parent and not isinstance(new_parent, SitemapTreeElement):
            raise TypeError('SitemapTreeElement type expected')
        self._parent = new_parent
        

class TextReferenceCrawlingInfo(ReferenceCrawlingInfo):
    """Class for clawling information about text reference. 
    At the current time we will only deal with text references."""

    def __init__(self, reference, depth, parent = None, title = ''):
        """Initializes text reference crawlong info properties.
        
        reference -- corresponding URL
        depth --     crawling depth of reference - number of clicks we need 
                     to do in order to reach a resourse corresponding to this 
                     reference from a websitesite homepage
        parent --    sitemap element which is intended to be a parent of a 
                     sitemap element corresponding to this reference 
                     (by default is None)
        title --     title of text reference (by default is '')
                    
        """

        ReferenceCrawlingInfo.__init__(self, reference, depth, parent)

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
        

class SiteSpiderError(Exception):
    """Base class for site spider errors."""

    pass


class ConnectionError(SiteSpiderError):
    """Class for Internet connection errors. Exceptions of this class are
    raised if site spider can't connect to given URL. Contains URL, connection
    to which was failed.
    
    """
    
    def __init__(self, url):
        self._url = url

    def __str__(self):
        return 'Unable to connect to %s' % self._url

    
class InvalidURLError(SiteSpiderError):
    """Class for errors connected with URL validity. Contains invalid URL,
    due to which exception was raised.
    
    """
    
    def __init__(self, url):
        self._url = url
        
    def __str__(self):
        return 'Invalid URL: %s' % self._url

    
class ResourseRetrieveError(SiteSpiderError):
    """Class for client or server errors, due to which site spider is unable
    to retrieve resourse corresponding to given URL. Contains URL, due to which
    exception was raised and 'exception' attribute for further error information
    wich is instance of urllib2.URLError class or its subclass.
    
    """
    
    def __init__(self, url, exception):
        self._url = url
        self._exception = exception
        
    def __str__(self):
        return 'Unable to retrieve resourse from %s: '% self._url + \
               str(self._exception)

    
class SiteSpider(object):
    """Site spider class. Site spider is intended to crawl given website with
    given preferences and to build a sitemap tree while crawling.
    
    """
    
    # Crawling statuses of site spider. They are used to recogniaize whether
    # clawling was finished successfully or not.
    CRAWLING_STATUS_SUCCESS = 1
    CRAWLING_STATUS_ERROR = 0
    
    def __init__(self, site_homepage_address, depth_limit = 0,
                 download_delay = 0, connection_attempts_number = 1,
                 connection_attempt_timeout = 0, robotstxt_obey = True):
        """Initializes site spider preferences.
        
        site_homepage_address --      URL of a website which is intended 
                                      to be crawled
        depth_limit --                crawling depth limit. References which 
                                      depth is grater then this parametr won't
                                      be crawled an won't be added to sitemap 
                                      tree. '0' means no depth limitation. 
                                      (by default is 0)
        download_delay --             average interval between site resourse 
                                      downloads. If nonzero, site spider will 
                                      use random dowload delay from 
                                      [0.5 * download_delay, 
                                      1.5 * download_delay]. 
                                      It is highly recommeded to set this 
                                      parametr in order not to override with 
                                      requests server of website you are giong
                                      to crawl. (by default is 0)
        connection_attempts_number -- maximum number of connection attempts 
                                      site spider will do in case of connection
                                      errors before dumping crawling process.
                                      (by default is 0)
        connection_attempt_timeout -- interval between connection attempts in 
                                      case of connection errors.
                                      (by default is 0)                              
        robotstxt_obey --             boolean parametr which states whether
                                      site spider will respect robots.txt 
                                      policies or not (by default is True)
                                      
        """
        
        # Set site spider name. It is used to form user-agent request header
        self._name = 'SiteSpider/1.0'


        # Check a type of 'site_homepage_address' parametr        
        if not isinstance(site_homepage_address, basestring):
            raise TypeError('string type expected')            
        # Set the allowed domain of spider. Spider is allowed to crawl only
        # with the limits of this domain.
        self._allowed_domain = self._normalize_homepage_address(
                                   site_homepage_address)
        
        # Check a type of 'depth_limit' parametr        
        if not isinstance(depth_limit, (int, long)):
            raise TypeError('int or long type expected')            
        self._depth_limit = depth_limit
                
        # Check a type of 'download_delay' parametr        
        if not isinstance(download_delay, (int, long)):
            raise TypeError('int or long type expected')            
        self._download_delay = download_delay
        # Set download delay bounds. Site spider will use random download
        # delay between this buonds.
        self._download_delay_upper_bound = 1.5 * self._download_delay
        self._download_delay_lower_bound = 0.5 * self._download_delay

        # Check a type of 'connection_attempts_number' parametr
        if not isinstance(connection_attempts_number, (int, long)):
            raise TypeError('int or long type expected')            
        self._connection_attempts_number = connection_attempts_number

        # Check a type of 'connection_attempt_timeout' parametr
        if not isinstance(connection_attempt_timeout, (int, long)):
            raise TypeError('int or long type expected')                        
        self._connection_attempt_timeout = connection_attempt_timeout
        
        self._robotstxt_obey = robotstxt_obey
        # Set a parser of robots.txt file which is provided by
        # python built-in library robotparser
        self._robotstxt_file_parser = robotparser.RobotFileParser()

        # Set request headers
        user_agent_header = self._name
        accept_header = \
                'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        self._request_headers = {
            'User-Agent': user_agent_header,
            'Accept': accept_header
        }
        
        # Set parser of web pages
        self._site_page_parser = SitePageParser()
        
        # self._references_crawling_info_schedule contains instances of 
        # ReferenceCrawlingInfo class corresponding to references that 
        # site spider have to process. Initialize it with an empty list
        self._references_crawling_info_schedule = []
        # self._viewed_references is a set of references that were 
        # already processed. Initialize it with an empty set
        self._viewed_references = set()
        
        # self._sitemap_tree contains sitemap tree (root element of this tree)
        # built by site spider. Initialize it with None
        self._sitemap_tree = None
                
        # self._crawling_status contains current crawling status of a 
        # site spider. Crwaling is not started, so initialize it with None
        self._crawling_status = None
 
        # Initialize random number generator in order to use it in order
        # to randomize dawnload delay
        random.seed()

        
    def _normalize_homepage_address(self, site_homepage_address):
        """Normalizes given site homepage address - if address has no 
        URL scheme, defines it as 'http', cuts the path and quers parts of URL 
        and adds tracing slash if needed.
        
        site homepage address -- corresponding URL
        
        Returns normalized URL.
        
        """
        
        # Split URL into parts
        address_parts = urlparse.urlsplit(site_homepage_address, 
                                          allow_fragments = False)
        scheme = address_parts.scheme
        netloc = address_parts.netloc
        path = address_parts.path
        query = address_parts.query

        # If originally there was no URL scheme, urlparse.urlsplit will
        # recognize netloc part as path part of URL. We need to improve it
        # Also we set 'http' scheme as default URL scheme in this case
        if not scheme:
            scheme = 'http'
            path_slash_position = path.find('/')
            if path_slash_position != -1:
                netloc = path[ : path_slash_position]
                path = path[path_slash_position : ]
            else:
                netloc = path
                path = ''
        # Cut the query part if needed
        if query:
            query = ''
        # Cut path part and add tracing '/' if needed
        path_slash_position = path.find('/')
        if path_slash_position != -1:
            path = path[ : path_slash_position + 1]
        else:
            path += '/'

        # Build normalized URL
        normalized_address_parts = (scheme, netloc, path, query, 
                                    address_parts.fragment)
        normalized_address = urlparse.urlunsplit(normalized_address_parts)
        return normalized_address
    
    def _download_site_resourse(self, reference):
        """Dawnloads site resourse by given reference.
        
        reference -- corresponding URL
        
        Returns file-like object, containing requsted resourse.
        Raises InvalidURLError exception in case of invalid URL, 
        ConnectionError exception in case of connection errors
        and ResourseRetrieveError in case of impossibility of 
        resourse retrieval.
        
        """
        
        # Form the request
        request = urllib2.Request(reference, headers = self._request_headers)

        # Resourse is not downloaded yet and it's the first attempt to do it
        resourse_is_recieved = False
        connection_attempt_number = 1
        resourse = None

        # Try to download resourse
        while not resourse_is_recieved:
            try:
                resourse = urllib2.urlopen(request)
            except (httplib.InvalidURL, exceptions.ValueError):
                # Given URL is invalid
                raise InvalidURLError(reference)
            except httplib.NotConnected:
                # Connection was not established
                # Check number of a connection attempt
                if connection_attempt_number < self._connection_attempts_number:
                    logging.error('Connection to ' + reference + 
                                  ' failed, trying to connect again')
                    connection_attempt_number += 1
                    time.sleep(self._connection_attempt_timeout)
                else:
                    raise ConnectionError(reference)            
            except (urllib2.URLError, httplib.HTTPException, 
                    exceptions.IOError), error:
                # Check the nature of a raised exception
                if hasattr(error, 'reason') and \
                        isinstance(error.reason, socket.error):
                    # Connection also was not established (but another 
                    # exception is raised by urllib2)
                    # Check number of a connection attempt
                    if connection_attempt_number < self._connection_attempts_number:
                        logging.error('Connection to ' + reference + 
                                      ' failed, trying to connect again')
                        connection_attempt_number += 1
                        time.sleep(self._connection_attempt_timeout)
                    else:
                        raise ConnectionError(reference)
                else:
                    # Another error happend due to wich site spider is
                    # unable to download requested resourse
                    raise ResourseRetrieveError(reference, error)
            else:
                # Resourse was downloaded succesfully
                resourse_is_recieved = True
        return resourse

    def _parse_robotstxt_file(self, robotstxt_file):
        """Feeds robotstxt file to site spider robots.txt file parser.
        
        robotstxt_file -- file-like object containing robots.txt file contents
        
        """
        
        # Get lines of robotstxt file and feed it to parser
        robotstxt_lines = [line.strip() for line in robotstxt_file]
        self._robotstxt_file_parser.parse(robotstxt_lines)

    def _normalize_reference(self, reference):
        """Normalizes reference - makes it absolute and 
        adds tracing slash if needed
        
        reference -- corresponding URL
        
        Returns normalized URL
        """
        
        # Split URL to parts
        reference_parts = urlparse.urlsplit(reference, allow_fragments = False)
        scheme = reference_parts.scheme
        path = reference_parts.path
        normalized_reference = reference

        # Add tracing '/' if there no query part of URL and no file extention
        # in the path part of URL
        if not reference_parts.query and '.' not in path:
            if not path.endswith('/'):
                path += '/'
                reference_parts = (scheme, reference_parts.netloc, path, 
                                   reference_parts.query, reference_parts.fragment)
                normalized_reference = urlparse.urlunsplit(reference_parts)

        # Make URL absolute if it is relative
        if not scheme:
            normalized_reference = urlparse.urljoin(self._allowed_domain, 
                                    normalized_reference)
        return normalized_reference
    
    def _normalize_reference_parsing_info(self, reference_parsing_info):
        """Normalizes given parsing information about reference. 
        Actually, normalizes reference in this parsing information.
        
        reference_parsing_info -- ReferenceParsingInfo class or its subclass 
                                  instance containing reference 
                                  parsing information
                                  
        Returns ReferenceParsingInfo class or its subclass instance with 
        normalized reference.
        
        """
        
        reference = reference_parsing_info.reference
        normalized_reference = self._normalize_reference(reference)
        reference_parsing_info.reference = normalized_reference
        return reference_parsing_info
    
    def _filter_reference(self, reference):
        """Filtrs given reference. Discards reference if it leads out of 
        crawling website or the resourse it leads to is not a website page 
        or it was already processed by site spider or it is already put in
        schedule in order to process later.
        
        reference -- corresponding URL
        
        Returns given URL back if given reference was not discarded or 
        None otherwise
        
        """
        
        if self._allowed_domain not in reference:
            logging.info('Filtered offsite reference: %s' % reference)
            return None
        reference_parts = urlparse.urlsplit(reference)
        if '.' in reference_parts.path:
            if not reference_parts.path.endswith('.html') and \
                    not reference_parts.path.endswith('.htm') and \
                    not reference_parts.path.endswith('.xhtml') and \
                    not reference_parts.path.endswith('.xht') and \
                    not reference_parts.path.endswith('.xml') and \
                    not reference_parts.path.endswith('.php'):
                logging.info('Filtered reference (unsuitable file format): %s' %
                             reference)
                return None

        if reference in self._viewed_references:
            return None
        
        for reference_crawling_info in self._references_crawling_info_schedule:
            if reference_crawling_info.reference == reference:
                return None
        return reference
    
    def _filter_reference_parsing_info(self, reference_parsing_info):
        """Filters given parsing information of reference by its value.
        Discards parsing information if reference was discarded by
        _filter_reference method.

        reference_parsing_info -- ReferenceParsingInfo class or its subclass 
                                  instance containing reference 
                                  parsing information
                                  
        Returns back given instance if parsing information was not discarded
        or None otherwise.
        
        """
        
        reference = reference_parsing_info.reference
        if not self._filter_reference(reference):
            return None
        return reference_parsing_info
        
    def _add_sitemap_tree_element(self, element_class, element_depth, 
                                  element_parent, **kwargs):
        """Adds new sitemap element to sitemap tree.
        
        element_class --  class of added element (HeadlineElement or 
                          TextReferenceElement)
        element_depth --  crawling depth of added element
        element_parent -- sitemap tree element which is intended to be a parent
                          of added element
        **kwargs --       dictionry with other element parametrs specified for 
                          its class
        
        Returns added sitemap element.
        
        """

        # Create new sitemap element corresponding to given element class
        if element_class is HeadlineElement:
            element_headline = kwargs['headline']
            new_element = HeadlineElement(element_headline, element_depth, 
                                          element_parent)
        elif element_class is TextReferenceElement:
            element_reference = kwargs['reference']
            element_title = kwargs['title']
            new_element = TextReferenceElement(element_reference, element_title, 
                                               element_depth, element_parent)
 
        # Check whether added element is root of sitemap tree or not
        if element_parent:
            element_parent.append_child(new_element)
        else:
            self._sitemap_tree = new_element
        return new_element

    def _delay(self):
        """Delays site spider. Delay interval is a random number between
        bounds that were set while initialization.
        
        """
        
        download_delay = random.uniform(self._download_delay_upper_bound,
                          self._download_delay_lower_bound)
        time.sleep(download_delay)
        
    
    def crawl(self):
        """Main site spider method. Manages the process of crawling and
        building sitemap tree.
        
        """
        
        # Start crawling process
        logging.info('Crawling started (bot %s)' % self._name)        
        self._crawling_status = self.CRAWLING_STATUS_SUCCESS
        
        # Test connection to given website
        # If it is failed, there is no point to continue crawling
        try:
            self._download_site_resourse(self._allowed_domain)
        except ConnectionError, error:
            logging.critical(str(error))
            logging.critical('Crawling dumped (bot %s)' % self._name)
            
            # Inform user abuot a failure
            print error

            # Dump crawling
            self._crawling_status = self.CRAWLING_STATUS_ERROR
            return
        
        except SiteSpiderError, error:
            logging.critical(str(error))
            logging.critical('Crawling dumped (bot %s)' % self._name)

            # Inform user abuot a failure
            print error
            
            # Dump crawling
            self._crawling_status = self.CRAWLING_STATUS_ERROR
            return

        # Delay spider if corresponding parametr it is stated
        if self._download_delay:
            self._delay()
        
        # Try to retrieve and parse robots.txt file if corresponding 
        # parametr it is stated
        if self._robotstxt_obey:
            # Defile robots.txt file location
            robotstxt_file_url = urlparse.urljoin(self._allowed_domain, 
                                  '/robots.txt')
            try:
                robotstxt_file = self._download_site_resourse(
                                  robotstxt_file_url)
            except SiteSpiderError, error:
                # robots.txt file was not downloaded
                logging.warning('Unable to retrieve robots.txt file')
                self._robotstxt_obey = False
            else:
                # Parse robots.txt file
                self._parse_robotstxt_file(robotstxt_file)
                logging.info('File robots.txt retrieved and parsed')

                # Delay spider if corresponding parametr it is stated  
                if self._download_delay:
                    self._delay()

        # Set start reference crawling information
        start_reference = self._allowed_domain
        start_reference_depth = 0
        start_reference_crawling_info = TextReferenceCrawlingInfo(start_reference, 
                                         start_reference_depth)
        self._references_crawling_info_schedule.append(start_reference_crawling_info)
        
        # Main crawling loop
        while self._references_crawling_info_schedule:
            # Get next reference crawling information
            reference_crawling_info = self._references_crawling_info_schedule.pop()
            reference = reference_crawling_info.reference
            reference_depth = reference_crawling_info.depth
            reference_title = reference_crawling_info.title
            reference_parent = reference_crawling_info.parent

            # Check depth of reference
            if self._depth_limit and reference_depth > self._depth_limit:
                logging.info('Ignoring link (depth > %d): %s' % 
                        (self._depth_limit, reference))
                continue
            
            # Check whether reference was already processed
            if reference in self._viewed_references:
                continue
            
            # We oly deal with text references. But if reference is not a text
            # reference it has no title. In this case we'll suppose that title
            # of reference is a title of page it leads to.
            # So, if reference has title and depth limit is stated and reference
            # depth is equal to depth limit, there is no need to dowload the 
            # page that reference leads to. 
            # Otherwise, we have to download it
            if not reference_title or \
                    (self._depth_limit and reference_depth != self._depth_limit):

                # Before downloading we have to check if it is allowed by
                # robots.txt file
                if self._robotstxt_obey and \
                        not self._robotstxt_file_parser.can_fetch(self._name, 
                                                                  reference):
                    logging.info(
                            'Filtered reference (forbidden by robots.txt): %s' % 
                            reference)
                    continue

                # Try to download the page
                try:
                    page = self._download_site_resourse(reference)
                except ConnectionError, error:
                    # Problems with connection, spider unable to 
                    # continue crawling
                    logging.critical(str(error))
                    logging.critical('Crawling dumped (bot %s)' % self._name)

                    # Inform user abuot a failure
                    print error

                    # Dump crawling
                    self._crawling_status = self.CRAWLING_STATUS_ERROR
                    return
                except SiteSpiderError, error:
                    # Other problems with downloading. It may be a single error
                    # cased by current reference. So spider have to continue
                    # crawling.
                    logging.error(str(error))
                    continue
                
                # Page downloaded successfully
                logging.info('Crawled: %s' % reference) 

                # Delay spider if corresponding parametr it is stated
                if self._download_delay:
                    self._delay()
                
                # Try to parse downloaded page
                try:
                    page_parsing_info = self._site_page_parser.parse_site_page(
                                         page.read())
                except SitePageParseError, parse_error:
                    # Parse error. Spider have to continue crawling.
                    logging.error(str(parse_error))
                    continue
                
                # Page persed succesfully
                logging.info('Parsed: %s' % reference)
                
                # Try to get page title if current reference has no title
                if not reference_title:
                    reference_title = page_parsing_info.title
            
            # But it may happen that downoaded page has no title. 
            # Because at the current time we support only text references we
            # can't add this reference to the sitemap
            if not reference_title:
                logging.warning(
                        'Reference has no title, can`t add to sitemap: %s' % 
                        reference)
                continue
            
            # Otherwise, add text reference element to the sitemap
            new_text_reference_element = self._add_sitemap_tree_element(
                                          TextReferenceElement, 
                                          reference_depth, reference_parent, 
                                          reference = reference,
                                          title = reference_title)
            self._viewed_references.add(reference)
            logging.info('Added sitemap text reference element: %s, %s' % 
                    (reference_title, reference))
            
            # If depth limit is stated and we have reached it, there is no need
            # to process reference groups and their titles that were retrieved
            # from parsed page
            if not self._depth_limit or reference_depth != self._depth_limit:
                # Set haedlines paramentrs
                healine_elements_parent = new_text_reference_element
                headline_elements_depth = reference_depth + 1

                # Process groups of references retrieved from parsed page
                page_references_groups = page_parsing_info.references_groups
                for references_group in page_references_groups:
                    # Get references parsing info of reference group
                    references_parsing_info = references_group.references
                    # Normalize this parsing info
                    normalized_references_parsing_info = map(
                            self._normalize_reference_parsing_info,
                            references_parsing_info)
                    # Filter this parsing info
                    filtered_references_parsing_info = filter(
                            self._filter_reference_parsing_info,
                            normalized_references_parsing_info)
                    # If there still references in references group after
                    # filtering, we have to process them
                    if filtered_references_parsing_info:
                        # Check if current group of references has a headline
                        refences_group_headline = references_group.headline
                        if refences_group_headline:
                            # Add healine element to the sitemap
                            new_headline_element = \
                                    self._add_sitemap_tree_element( 
                                            HeadlineElement, 
                                            headline_elements_depth,
                                            healine_elements_parent,
                                            headline = refences_group_headline)
                            logging.info('Added sitemap headline element: %s' % 
                                    refences_group_headline)
                            # Set this element as a parent of references in 
                            # current group
                            text_reference_elements_parent = \
                                    new_headline_element
                            
                        else:
                            # Otherwise, set added text reference element as 
                            # a parent of references in current group
                            text_reference_elements_parent = \
                                    healine_elements_parent

                        # Depth of new text refernce elements is depth of
                        # last added text reference element + 1
                        text_reference_elements_depth = reference_depth + 1

                        # Reverse list with references parsing information
                        # In order to process referencs in the same order 
                        # as they follow each other on the site page
                        filtered_references_parsing_info.reverse()
                        
                        # Process references group
                        for reference_parsing_info in \
                                filtered_references_parsing_info:
                            # Create text reference crawling information
                            reference = reference_parsing_info.reference
                            reference_title = reference_parsing_info.title
                            reference_crawling_info = \
                                    TextReferenceCrawlingInfo(reference,
                                            text_reference_elements_depth,
                                            text_reference_elements_parent,
                                            reference_title)
                            # And put apend it to schedule in order to process
                            # later
                            self._references_crawling_info_schedule.append(
                                    reference_crawling_info)
            
        # Finish crawing process                  
        logging.info('Crawling finished (bot %s)' % self._name) 
                            
                            
    @property
    def sitemap_tree(self):
        """Returns sitemap tree created by site spider while crawling."""
        
        return self._sitemap_tree
       
    @property
    def crawling_status(self):
        """Returns current crawling state of site spider."""
        
        return self._crawling_status
                
    