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

__all__ = ['species', 'element', 'reaction']

import numpy as np
try:
    from astropy.table import Table
    use_astropy = True
except (ImportError):
    use_astropy = False

import numpy as _np


#~ The urllib2 module has been split across several modules in Python 3.0
#~ named urllib.request and urllib.error. The 2to3 tool will automatically adapt imports when converting your sources to 3

# used for Python 2: 
# urllib.urlencode
# urllib2.Request
# urllib2.urlopen

try:
    # For Python 3.0 and later
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode
    from html import parser
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib import urlencode
    from urllib2 import urlopen, Request
    from HTMLParser import HTMLParser
#######################
# General settings

KIDA_BASE_URL = 'http://kida.obs.u-bordeaux1.fr/'

SPECIES_SEARCH = 'results_species/l/'
ELEMENT_SEARCH = 'results_species_contains/l/'
REACTION_SEARCH = 'search_reaction/l/'

TIMEOUT = 30

#######################
# SEARCHES

# Species search

def species(name, stype = 'common'):
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
    results = _get_results(parameters, url=path)
    
    return None


def element(name, charge = ['positive', 'negative', 'neutral']):
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
    results = _get_results(parameters, url=path)
    return results

def reaction(name, stype):
    return None

#######################
# Parsing functions

def _parse_charge(charge):
    charge_list = [ ]
    li_names = [ 'positive', 'negative', 'neutral' ]
    reply = [ ['', 'ok'][i in charge] for i in li_names ]
    charge_list = [ (i,j) for i,j in zip(li_names, reply) ]
    return charge_list

def _parse_results(results):
    return None

#######################
# url and results handling

def _get_results(parameters, url, timeout=TIMEOUT):
    parameters = urlencode(parameters)
    req = Request(url, parameters)
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    results = urlopen(req, timeout=timeout).read()
    return results

#######################


