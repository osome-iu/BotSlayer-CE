#!/usr/bin/evn python3
import re
import spacy
from spacy.tokenizer import Tokenizer
from spacy.util import compile_prefix_regex, compile_infix_regex, compile_suffix_regex


def get_twitter_tokenizer(nlp):
    excluded_symbols = {'\\$', '#', '@'}
    prefixes = tuple(
        [
            s for s in nlp.Defaults.prefixes
            if s not in excluded_symbols
        ]
    ) + ('‘', '“', '’')

    suffixes= ('’', '”', '’', ) + nlp.Defaults.suffixes

    infixes = ('‘', '’', '“', '”', '’',) + nlp.Defaults.infixes

    prefix_search = compile_prefix_regex(prefixes).search
    suffix_search = compile_suffix_regex(suffixes).search
    infix_finditer= compile_infix_regex(infixes).finditer
    url_match = re.compile(r'''^http(?:s*)?://''').match

    return Tokenizer(nlp.vocab,
        prefix_search=prefix_search,
        suffix_search=suffix_search,
        infix_finditer=infix_finditer,
        token_match=url_match)



def test_main():
    '''
        Usage of the function
    '''
    nlp = spacy.load('en')
    nlp.tokenizer = get_twitter_tokenizer(nlp)

    print([token.text for token in nlp(
        '''RT @XX : @YY Dear’a Sir, Given our love &amp of #cats, we trust https://t.co/OjgvGATUSu $USD.''')])



if __name__ == '__main__': test_main()
