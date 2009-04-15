import unittest
import os
import difflib            as diff
from   random             import choice, randint, shuffle

from   nose.tools         import assert_equal

from   zwiki.zwlexer      import ZWLexer
from   zwiki.zwparser     import ZWParser
from   zwiki.test.testlib import ZWMARKUP, ZWMARKUP_RE, \
                                 gen_psep, gen_ordmark, gen_unordmark, \
                                 gen_headtext, gen_texts, gen_row, \
                                 gen_wordlist, gen_words, gen_linkwords, gen_links,\
                                 gen_macrowords, gen_macros, \
                                 random_textformat, random_listformat, \
                                 random_tableformat, random_wikitext, random_wiki


stdfiles_dir    = os.path.join( os.path.split( __file__ )[0], 'stdfiles' )
rndfiles_dir    = os.path.join( os.path.split( __file__ )[0], 'rndfiles' )
samplefiles_dir = os.path.join( os.path.split( __file__ )[0], 'samplefiles' )
zwparser        = None
words           = None
links           = None
macros          = None

def setUpModule() :
    global zwparser, words, links, macros
    print "Initialising the parser ..."
    zwparser     = ZWParser( lex_optimize=True, yacc_debug=True,
                           yacc_optimize=False )
    print "Initialising wiki ..."
    wordlist     = gen_wordlist( maxlen=20, count=200 )
    words        = gen_words( wordlist, count=200, huri_c=10, wuri_c=10 )
    print "Initialising links ..."
    linkwords    = gen_linkwords( maxlen=50, count=200 )
    links        = gen_links( linkwords, 100 )
    print "Initialising macros ..."
    macrowords   = gen_macrowords( maxlen=50, count=200 )
    macros       = gen_macros( macrowords, 100 )
    
def tearDownModule() :
    pass

class TestWikiDumpsRandom( object ) :
    """Test cases to validate ZWiki random"""

    def _test_execute( self, type, testcontent, count ) :
        testcontent = zwparser.preprocess( testcontent )
        try :
            tu      = zwparser.parse( testcontent, debuglevel=0 )
            result  = tu.dump()[:-1]
        except :
            tu     = zwparser.parse( testcontent, debuglevel=2 )
            result = tu.dump()[:-1]
        if result != testcontent :
            print ''.join(diff.ndiff( result.splitlines(1), testcontent.splitlines(1) ))
        assert result == testcontent, type+'... testcount %s'%count

    def test_1_textformatting( self ) :
        """Testing by randomly injecting wiki text formatting markup"""
        print "Testing by randomly injecting wiki text formatting markup"
        newlines = [ '\n' ] * 5 
        testlist = [ random_textformat( words + newlines, links, macros, 200 ) 
                     for i in range(100) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'rnd_textformatting', t, testcount
            testcount += 1

    def test_2_listformatting( self ) :
        """Testing by randomly injecting wiki text formatting and list markup"""
        print "\nTesting by randomly injecting wiki text formatting and list markup"
        testlist = [ '#\n' ] + \
                   [ random_listformat( words, links, macros, '\n', 200 ) 
                     for i in range(100) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'rnd_listformatting', t, testcount
            testcount += 1

    def test_3_tableformatting( self ) :
        """Testing by randomly injecting wiki text formatting and table markup"""
        print "\nTesting by randomly injecting wiki text formatting and table markup"
        testlist = [ random_tableformat( words, links, macros, '\n', 200 ) 
                     for i in range(100) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'rnd_tableformatting', t, testcount
            testcount += 1

    def test_4_wikitext( self ) :
        """Testing by randomly generating wiki words and markups"""
        print "\nTesting by randomly generating wiki words and markups"
        testlist = [ random_wikitext( words, links, macros, 200 ) 
                     for i in range(500) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'rnd_wikitext', t, testcount
            testcount += 1

    def test_5_wiki( self ) :
        """Testing by randomly generating wiki"""
        print "\nTesting by randomly generating wiki"
        testlist = [ random_wiki( 1000 ) for i in range(500) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'rnd_wiki', t, testcount
            testcount += 1