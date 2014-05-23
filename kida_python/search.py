# Interact with the online KIDA database
# http://kida.obs.u-bordeaux1.fr/

# 2 different searches and 2 downloads possible
# 1. Species
#       -by species
#       -by element
# 2. Reactions
# Download list of reactions
#       -Uni and Biomolecular reactions
#       -Termolecular reactions

#####################
# Imports

__all__ = ['query_species', 'query_element', 'query_reaction']

try:
    from astropy.table import Table
    use_astropy = True
except (ImportError):
    use_astropy = False

import numpy as _np

# NOTE:
# The urllib2 module has been split across several modules in Python 3.0
# named urllib.request and urllib.error. The 2to3 tool will automatically
# adapt imports when converting your sources to 3

# What is used for Python 2: 
# urllib.urlencode
# urllib2.Request
# urllib2.urlopen

try:
    # For Python 3.0 and later
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode
    #from html import parser as htmlparser
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib import urlencode
    from urllib2 import urlopen, Request
    #from HTMLParser import HTMLParser as htmlparser


from lxml import html


#######################
# General settings

KIDA_BASE_URL = 'http://kida.obs.u-bordeaux1.fr/'

SPECIES_SEARCH = 'results_species/l/'
ELEMENT_SEARCH = 'results_species_contains/l/'
REACTION_SEARCH = 'search_reaction/l/'
# Timeout in seconds
TIMEOUT = 30

#######################
# NOTES

"""
From astroquery API doc.

Common keywords to implement:
    return_query_payload - Return the POST data that will be submitted as a dictionary
    savename - [optional - see discussion below] File path to save the downloaded query to
    timeout - timeout in seconds

Directory Structure:

    module/
    module/__init__.py
    module/core.py
    module/tests/test_module.py

__init__.py contains:

    from astropy.config import ConfigurationItem

    SERVER = ConfigurationItem('Service_server', ['url1','url2'])

    from .core import QueryClass

    __all__ = ['QueryClass']

core.py contains:

    from ..utils.class_or_instance import class_or_instance
    from ..utils import commons, async_to_sync

    __all__ = ['QueryClass']  # specifies what to import

    @async_to_sync
    class QueryClass(astroquery.BaseQuery):

        server = SERVER()

        def __init__(self, *args):
            # set some parameters 
            # do login here
            pass

        @class_or_instance
        def query_region_async(self, *args, get_query_payload=False):

            request_payload = self._args_to_payload(*args)

            response = commons.send_request(self.server, request_payload, TIMEOUT)

            # primarily for debug purposes, but also useful if you want to send
            # someone a URL linking directly to the data
            if get_query_payload:
                return request_payload

            return result

        @class_or_instance
        def get_images_async(self, *args):
            image_urls = self.get_image_list(*args)
            return [get_readable_fileobj(U) for U in image_urls]
            # get_readable_fileobj returns need a "get_data()" method?

        @class_or_instance
        def get_image_list(self, *args):

            request_payload = self.args_to_payload(*args)

            result = requests.post(url, data=request_payload)

            return self.extract_image_urls(result)

        def _parse_result(self, result):
            # do something, probably with regexp's
            return astropy.table.Table(tabular_data)

        def _args_to_payload(self, *args):
            # convert arguments to a valid requests payload

            return dict

"""

#######################
# SEARCHES

# Species search

def query_species(name, stype = 'common', timeout=TIMEOUT):
    """
    name : name of species, case sensitive, e.g. H2O for water
    stype : search type, 'common', 'exact' or 'inchi'
            common - common name, formula (isomers)
            exact - exact formula
            inchi - inchi code (IUPAC International Chemical Identifier)

    Note, searching by inchi code does not seem to work well...
        
    """
    #~ species_input_name = name
    #~ typeSearch = stype
    parameters = []
    
    parameters.extend( [('species_input_name', name)] )
    #~ parameters.extend( )

    path = KIDA_BASE_URL + SPECIES_SEARCH
    results = _get_page(parameters, url=path, timeout=timeout)
    details, formula, name, e_state = _parse_results_species(results)
    return details, formula, name, e_state


def query_element(name, charge = ['positive', 'negative', 'neutral'], timeout=TIMEOUT):
    """
    name : species contains the element with name
    charge : list with at least one of the following
            'positive' : positive charge
            'negative' : negative charge
            'neutral' : neutral charge
            default is all of them
    """
    # the base url for the search
    path = KIDA_BASE_URL + ELEMENT_SEARCH
    # now create the parameter list
    parameters = []
    parameters.extend( [('species_input_name', name)] )
    parameters.extend( _parse_charge(charge) )
    results = _get_page(parameters, url=path, timeout=timeout)
    details, formula, name, e_state = _parse_results_species(results)
    return details, formula, name, e_state

def query_reaction(name, stype, timeout=TIMEOUT):
    return None

#######################
# url and results handling

def _get_page(parameters, url, timeout):
    parameters = urlencode(parameters)
    req = Request(url, parameters)
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    results = urlopen(req, timeout=timeout).read()
    return results

#######################
# Parsing functions

def _parse_charge(charge):
    charge_list = [ ]
    li_names = [ 'positive', 'negative', 'neutral' ]
    reply = [ ['', 'ok'][i in charge] for i in li_names ]
    charge_list = [ (i,j) for i,j in zip(li_names, reply) ]
    return charge_list

def _page_parse_species(htmlpage):
    """
    Parses one html page of the results from KIDA
    when searching for species
    """
    tree = html.fromstring(htmlpage)
    # get the details. this is for one page only
    # the class attribute is weird with respect
    # to the column name in the actual page
    # changed to conform with page instead of attributes
    # so name = desc, formula = name[0], e_state = name[1]    
    species_details = tree.xpath('//span[@class="species_details"]//@href')
    species_name = tree.xpath('//td[@class="species_name"]//text()')
    species_name = [i.strip('\n').strip('\t') for i in species_name]
    species_name = [i.strip('\n').strip('\t') for i in species_name]
    species_formula = species_name[::2]
    species_e_state = species_name[1::2]
    species_desc = tree.xpath('//td[@class="species_desc"]//text()')
    species_name = [i.strip('\n').strip('\t') for i in species_desc]
    return species_details, species_formula, species_name, species_e_state


def _parse_results_species(htmlresults):
    """
        This function should parse a html result page from KIDA,
        to an array. In summary it should:
            - Get each result page that came out
            - Scrape each result page, get all links
            - Follow each element link in the results and scrape
              the details of the specific molecule into the array
        All levels of the array should be accessible, so that e.g.
        one should be able to get e.g. the dipole moment for all species
        that contains the H- ion.
        
    """
    # get number of pages and the links to them
    tree = html.fromstring(htmlresults)
    last_page = tree.xpath('//span[@class="pagination-element"]//@href')[-1]
    # gb is just GarBage
    gb, stype, n_last, stext = last_page.split('/')
    pnum = _np.arange(1,int(n_last)+1)
    urls = [KIDA_BASE_URL +'/'.join([stype, str(i), stext]) for i in pnum]
   
    # define lists for results
    details, formula, name, e_state = [],[],[],[]
    # loop through the pages and append the results
    for url in urls:
        results = _get_page([], url, timeout=TIMEOUT)
        results = _page_parse_species(results)
        # append page table columns to lists
        [details.append(i) for i in results[0]]
        [formula.append(i) for i in results[1]]
        [name.append(i) for i in results[2]]
        [e_state.append(i) for i in results[3]]
    return details, formula, name, e_state





