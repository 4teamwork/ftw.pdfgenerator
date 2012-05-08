from Products.CMFCore.utils import getToolByName


LANGUAGE_CODE_TO_OPTION_MAPPING = {
    'af': 'afrikaans',
    'eu': 'basque',
    'br': 'breton',
    'bg': 'bulgarian',
    'ca': 'catalan',
    'hr': 'croatian',
    'cs': 'czech',
    'da': 'danish',
    'nl': 'dutch',
    'en': 'english',
    'en-us': 'USenglish',
    'en-as': 'american',
    'en-gb': 'british',
    'en-ca': 'canadian',
    'en-au': 'australian',
    'en-nz': 'newzealand',
    'eo': 'esperanto',
    'et': 'estonian',
    'fi': 'finnish',
    'fr': 'french',
    'fr-ca': 'canadian',
    'gl': 'galician',
    'de': 'ngerman',
    'de-at': 'naustrian',
    'de-de': 'ngerman',
    'de-ch': 'ngerman',
    'el': 'greek',
    'he': 'hebrew',
    'hu': 'hungarian',
    'is': 'icelandic',
    'ia': 'interlingua',
    'ga': 'irish',
    'it': 'italian',
    'la': 'latin',
    'no': 'nynorsk',
    'pl': 'polish',
    'pt-br': 'brazilian',
    'pt': 'portuges',
    'ro': 'romanian',
    'ru': 'russian',
    'gd': 'scottish',
    'es': 'spanish',
    'sk': 'slovak',
    'sl': 'slovene',
    'sv': 'swedish',
    'sr': 'serbian',
    'tr': 'turkish',
    'uk': 'ukrainian',
    'cy': 'welsh',
    }


def lookup_babel_option(language_code):
    """Returns the babel option for a particular language code.
    Returns `None` if no option is found.
    """

    code = language_code

    if code in LANGUAGE_CODE_TO_OPTION_MAPPING:
        return LANGUAGE_CODE_TO_OPTION_MAPPING[code]

    if '-' in code:
        code = code.split('-')[0]
        if code in LANGUAGE_CODE_TO_OPTION_MAPPING:
            return LANGUAGE_CODE_TO_OPTION_MAPPING[code]

    return None


def get_preferred_babel_option_for_context(context):
    """Returns the preferred babel option (language) for the current context.
    It tries to get the language of the current context, secondary using the
    current preferred language of the current visitor.

    If no babel option is found, `None` is returned.
    """

    context_language_method = getattr(context, 'getLanguage', None)
    if context_language_method:
        language_code = context_language_method()

    else:
        ltool = getToolByName(context, 'portal_languages')
        language_code = ltool.getPreferredLanguage()

    return lookup_babel_option(language_code)
