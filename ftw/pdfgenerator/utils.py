from htmlentitydefs import name2codepoint as n2cp
from htmlentitydefs import codepoint2name as cp2n
import re
from zope.interface import directlyProvidedBy, directlyProvides


def provide_request_layer(request, layer):
    """ Add a layer interface on the request
    """
    layer = type(layer) == list and layer or [layer]
    ifaces = layer + list(directlyProvidedBy(request))

    # Since we allow multiple markers here, we can't use
    # zope.publisher.browser.applySkin() since this filters out
    # IBrowserSkinType interfaces, nor can we use alsoProvides(), since
    # this appends the interface (in which case we end up *after* the
    # default Plone/CMF skin)
    directlyProvides(request, *ifaces)


def baseclasses(cls, bases=None):
    """Returns a flat list of all baseclasses according to the method
    resolution order. Includes `cls`.
    """
    if bases is None:
        bases = []

    bases.append(cls)

    for base in cls.__bases__:
        if base not in bases:
            baseclasses(base, bases)

    return bases


def decode_htmlentities(string):
    """
    Decodes html entities and xml entities.
    """
    entity_re = re.compile("&(#?)(\d{1,5}|\w{1,8});")

    def substitute_entity(match):
        ent = match.group(2)
        if match.group(1) == "#":
            return unichr(int(ent))

        else:
            cp = n2cp.get(ent)

            if cp:
                return unichr(cp)

            else:
                return match.group()

    return entity_re.subn(substitute_entity, string)[0]


def encode_htmlentities(string, encoding='utf-8'):
    """
    Encodes the string with html entities.
    """

    if isinstance(string, unicode):
        was_unicode = True
    else:
        was_unicode = False
        string = string.decode(encoding)

    string = string.replace('&', '&amp;')

    for codepoint, name in cp2n.items():
        if name != 'amp':
            string = string.replace(unichr(codepoint), '&%s;' % name)

    if not was_unicode:
        string = string.encode(encoding)
    return string


def html2xmlentities(string):
    """
    Converts htmlentities to xmlentities
    """

    xpr = re.compile('&(\w{1,8});')

    def substitute_entity(match):
        ent = match.group(1)
        if ent in n2cp.keys():
            return '&#%i;' % n2cp[ent]

        else:
            return match.group(0)

    return xpr.subn(substitute_entity, string)[0]


def xml2htmlentities(string):
    """
    Converts xmlentities to htmlentities
    """
    xpr = re.compile('&#(\d{1,5});')

    def substitute_entity(match):
        ent = int(match.group(1))
        if ent in cp2n.keys():
            return '&%s;' % cp2n[ent]

        else:
            return match.group(0)

    return xpr.subn(substitute_entity, string)[0]
