import sys
import logging

from site_spider import SiteSpider
from sitemap_html_writer import SitemapHtmlWriter, SitemapHtmlWriterError

__doc__ = """
This is Yandex hometask project developed by Tolmchev Alexander
The main goal of this project is to produce sitemap of a website by given URL 
"""

# Arguments that will cause printing a help line 
HELP_ARGUMENTS = ('help', 'h', '-h')

# Help line 
HELP_STRING = \
"""This is WebsiteVisualizer - application for creating sitemap of website

Usage: website_visualizer.py <site address> <output file name> [<depth limit>]
The result is a html file with a sitemap of a given website

Parametrs:
<site adress> --      url of a website, map of which you want to get
<output file name> -- name of an output html-file
<depth limit> --      this parametr restricts the depth of a sitemap tree
                      (depth of a website page is a number of clicks that you
                      need to do in order to reach this page from the website 
                      home page).It is an optional parametr, but it's highly 
                      recommended to set it in order to get a quite readable 
                      sitemap and restrict the time of website crawling if the 
                      visualized website is big enough.
                      0 also means no depth restriction.
"""

# Strings that contain messages informing user about process status
INVALID_PARAMETRS_STRING = "Invalid parametrs number"

HELP_OFFER_STRING = "Type 'help' or 'h' or '-h' for help"

DEPTH_LIMIT_ERROR_STRING = "<depth limit> parametr have to be a digit"

CRAWLING_PROCESS_LAUNCHED_STRING = \
"""Website crawling began. It will take some time.
How much - it depends on the website size and the depth limit you have stated. 
If the site is not too big or the depth limit is small it may take several 
minutes. Instead, crawling a large site with a large or no depth limit 
may take hours. So please, wait patiently.
"""

CRAWLING_PROCESS_ERROR_STRING = \
"""Please, check your Internet connection,the URL validity and website
operability and restart the application.
"""

WRITING_SITEMAP_TO_HTML_ERROR_STRING = "Error while writing sitemap to html."

SITEMAP_CREATION_ERROR_STRING = "Sitemap was not created."

# Dawnloading preferences. They was deduced experimentally
DOWNLOAD_DELAY = 15    
CONNECTION_ATTEMPTS_NUMBER = 5
CONNECTION_ATTEMPT_TIMEOUT = 10

# Entry point of application
def main():
    # Check if the only argumet is a help argument
    if len(sys.argv) == 2:
        if sys.argv[1] in HELP_ARGUMENTS:
            print HELP_STRING
            return
            
    # Check number of arguments
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print "Invalid parametrs number"
        print "Type 'help' or 'h' or '-h' for help"
        return
    
    site_address = sys.argv[1]
    output_file_name = sys.argv[2]

    # Check if depth limit argument is stated
    if len(sys.argv) == 4:
        depth_limit_string = sys.argv[3]    

        # Check depth limit argument for validity
        if not depth_limit_string.isdigit():
            print DEPTH_LIMIT_ERROR_STRING
            print HELP_OFFER_STRING
            return
        depth_limit = int(depth_limit_string)
    else:
        depth_limit = 0
        
    # Set logging parametrs
    logging_file_name = 'sitemap_visualizer.log'
    logging_format = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(filename = logging_file_name, format = logging_format, 
                        level = logging.INFO)  
    
    # Create a site spider
    site_spider = SiteSpider(site_address, depth_limit, 
                             DOWNLOAD_DELAY, 
                             CONNECTION_ATTEMPTS_NUMBER, 
                             CONNECTION_ATTEMPT_TIMEOUT)
    
    # Inform user about crawling process launch
    print CRAWLING_PROCESS_LAUNCHED_STRING

    # Launch crawling process
    site_spider.crawl()
    
    # Check crawling status
    site_spider_crawling_status = site_spider.crawling_status
    if site_spider_crawling_status != SiteSpider.CRAWLING_STATUS_SUCCESS:
        # Inform user about a failure
        print CRAWLING_PROCESS_ERROR_STRING
        print SITEMAP_CREATION_ERROR_STRING
    else:
        # Get sitemap tree
        sitemap_tree = site_spider.sitemap_tree

        # Create sitemap html writer
        sitemap_html_writer = SitemapHtmlWriter(sitemap_tree, output_file_name)
        
        # Try to write sitemap to html
        logging.info('Writing sitemap to html: %s' % output_file_name)
        try:
            sitemap_html_writer.write_sitemap_tree_to_html()
        except SitemapHtmlWriterError:
            print WRITING_SITEMAP_TO_HTML_ERROR_STRING
            print SITEMAP_CREATION_ERROR_STRING
        else:
            logging.info('Sitemap is writen to %s.' % output_file_name)    
            print 'Sitemap was written to', output_file_name
        
    print 'See', logging_file_name, 'for more details and error reports.'


if __name__ == "__main__":
    main()

