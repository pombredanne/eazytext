import logging
import unittest
import os
import difflib              as diff
import random
from   random               import choice, randint, shuffle

from   nose.tools           import assert_equal
import cElementTree         as et
from   pylons               import config

from   zwiki.zwlexer        import ZWLexer
from   zwiki.zwparser       import ZWParser
import zwiki.test.testlib   as testlib
from   zwiki.test.testlib   import ZWMARKUP, ZWMARKUP_RE, UNICODE, \
                                   gen_psep, gen_ordmark, gen_unordmark, \
                                   gen_bqmark, gen_defnmark, gen_btableline, \
                                   gen_headtext, gen_texts, gen_row, \
                                   gen_wordlist, gen_words, gen_linkwords, gen_links,\
                                   gen_macrowords, gen_macros, \
                                   gen_htmlwords, gen_htmls, gen_xwikinames, \
                                   log_mheader, log_mfooter, genseed

log             = logging.getLogger(__name__)
seed            = None
stdfiles_dir    = os.path.join( os.path.split( __file__ )[0], 'stdfiles' )
rndfiles_dir    = os.path.join( os.path.split( __file__ )[0], 'rndfiles' )
samplefiles_dir = os.path.join( os.path.split( __file__ )[0], 'samplefiles' )
words           = None
links           = None
macros          = None
htmls           = None
xwikinames      = None

crooked_heading ="""
=== hello = world
how are you
======= I am doing fine
How about your
=== Me too ========
"""

crooked_nowiki  ="""
{{{}}}
{{{ }}}
{{{
  }}}
{{{
    hello world
    {{{
          {{{
            }}}
{{{
    hi world
{{{
    hello world again"""

crooked_table  ="""
|=|=|=

|||=
|=||=

|
|

|
"""
crooked_btable = """
||{ { "style" : "color:green; background-color:#ffffcc;", "cellpadding" : "20", \
      "cellspacing" : "0", "border" : "5px",  \
      "caption" : "fruits and icecreams" }
||={ "color" : "black" } | Fruits 

||-{ "color" : "black" } | Fruits 

|| { "color" : "black" } | Fruits 

||={ "color" : "black" } | Fruits 

||{{ "color" : "black" } | Fruits 

||}
"""

definitionnewline = """
:h?O	O&5	"Z94U'e(h<6SNaynA	0b99n$e	_ukRiIT`y{hA#}2I::g
www.RN'uw\nRD8j;vd3NE&YHX-Db(OF;'E@Old=
"""

def _loginfo( info ) :
    log.info( info )
    print info

def setUpModule() :
    global words, links, macros, htmls, xwikinames, seed

    testdir = os.path.basename( os.path.dirname( __file__ ))
    testfile= os.path.basename( __file__ )
    seed    = config['seed'] and int(config['seed']) or genseed()
    random.seed( seed )
    testlib.random.seed(  seed )
    log_mheader( log, testdir, testfile, seed )
    _loginfo( "Initialising wiki ..." )
    wordlist= gen_wordlist( maxlen=20, count=200 )
    words   = gen_words( wordlist, count=200, huri_c=10, wuri_c=10 )
    _loginfo( "Initialising links ..." )
    linkwords    = gen_linkwords( maxlen=50, count=200 )
    links        = gen_links( linkwords, 100 )
    _loginfo( "Initialising macros ..." )
    macrowords   = gen_macrowords( maxlen=50, count=200 )
    macros       = gen_macros( macrowords, 100 )
    _loginfo( "Initialising htmls ..." )
    htmlwords    = gen_htmlwords( maxlen=50, count=200 )
    htmls        = gen_htmls( htmlwords, 100 )
    _loginfo( "Initialising wiki extension names ..." )
    xwikinames   = gen_xwikinames( 100 )
    
def tearDownModule() :
    testdir  = os.path.basename( os.path.dirname( __file__ ))
    testfile = os.path.basename( __file__ )
    log_mfooter( log, testdir, testfile )

class TestDumpsValid( object ) :
    """Test cases to validate ZWiki parser."""

    def _test_execute( self, type, testcontent, count, ref='' ) :
        # Initialising the parser
        zwparser     = ZWParser( lex_optimize=True, yacc_optimize=False, yacc_debug=False )
        # Prepare the reference.
        ref        = ref or testcontent
        ref        = zwparser.wiki_preprocess( ref )
        props, ref = zwparser._wiki_properties( ref )

        # Characterize the generated testcontent set the wikiproperties
        wikiprops  = {}
        testcontent= ( "@ %s " % wikiprops ) + '\n' + testcontent

        # Test by comparing the dumps
        try :
            tu      = zwparser.parse( testcontent, debuglevel=0 )
            result  = tu.dump()[:-1]
        except :
            tu     = zwparser.parse( testcontent, debuglevel=2 )
            result = tu.dump()[:-1]
        if result != ref :
            #open( 'result', 'w' ).write( result )
            #open( 'ref', 'w' ).write( ref )
            print ''.join(diff.ndiff( result.splitlines(1), ref.splitlines(1) ))

        assert result == ref, type+'... testcount %s'%count

        # Test by translating to html
        #tu   = zwparser.parse( testcontent, debuglevel=0 )
        #html = tu.tohtml()
        #et.fromstring( html ) 

    def test_0_file( self ) :
        """If file `ref` is available pick it and test it"""
        log.info( "If file `ref` is available pick it and test it" )
        testlist  = []
        ref       = os.path.isfile( 'ref' ) and open( 'ref' ).read()
        ref and testlist.append( ref )
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'ref', t, testcount
            testcount += 1

    def test_1_heading( self ) :
        """Testing heading markup"""
        print "Testing heading markup"
        log.info( "Testing heading markup" )
        headmarkup= [ '=' , '==', '===', '====', '=====' ]
        testlist  = [ choice(headmarkup) + gen_headtext( words ) +
                      choice( headmarkup + [ '' ] ) + gen_psep(3)
                        for i in range(50) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'heading', t, testcount
            testcount += 1

    def test_2_hrule( self ) :
        """Testing horizontal rule markup"""
        print "\nTesting horizontal rule markup"
        log.info( "Testing horizontal rule markup" )
        self._test_execute( 'horizontalrule', '----', 1 )

    def test_3_wikix( self ) :
        """Testing wiki extension markup""" 
        print "\nTesting wiki extension markup"
        log.info( "Testing wiki extension markup" )
        wikix_cont = '\n'.join([ choice(words) for i in range(randint(1,20)) ])
        testlist   = [ '{{{' + choice(xwikinames) + '\n' + wikix_cont + \
                       '\n}}}\n' + gen_psep(randint(0,3))
                       for i in range(1000) ]
        testcount  = 1
        for t in testlist :
            yield self._test_execute, 'wikix', t, testcount
            testcount += 1

    def test_4_escapenewline( self ) :
        """Testing wiki text containing `~~\\n`"""
        print "\nTesting wiki text containing `~~\\n`"
        log.info( "Testing wiki text containing `~~\\n`" )
        testlist = [ ('hello ~~\nworld', 'hello \nworld') ]
        testcount = 1
        for t, r in testlist :
            yield self._test_execute, 'escapenewline', t, testcount, r
            testcount += 1

    def test_5_lastcharesc( self ) :
        """Testing wiki text with last char as `~`"""
        print "\nTesting wiki text with last char as `~`"
        log.info( "\nTesting wiki text with last char as `~`" )
        testlist = [ ('hello world~', 'hello world')  ]
        testcount = 1
        for t,r in testlist :
            yield self._test_execute, 'lastcharesc', t, testcount, r
            testcount += 1

    def test_6_textlines( self ) :
        """Testing textlines"""
        print "\nTesting textlines"
        log.info( "Testing textlines" )
        testlist  = [ '\n'.join([ gen_texts(
                                    words, links, macros, htmls,
                                    tc=5, pc=1, ec=2, lc=1, mc=1, hc=1, fc=1,
                                    nopipe=True
                                  )
                                  for j in range(randint(0,10)) ]) +
                      gen_psep(randint(0,3)) for i in range(100) ]  +\
                    [ '\n'.join([ gen_texts(
                                    words, links, macros, htmls,
                                    tc=5, pc=1, ec=2, lc=1, mc=1, hc=1, fc=0,
                                    nopipe=True
                                  )
                                  for j in range(randint(0,10)) ]) +
                      choice(ZWMARKUP) + ' ' +
                      '\n'.join([ gen_texts(
                                    words, links, macros, htmls,
                                    tc=5, pc=1, ec=2, lc=1, mc=1, hc=1, fc=0,
                                    nopipe=True
                                  )
                                  for j in range(randint(0,10)) ]) +
                      choice(ZWMARKUP) + ' ' 
                      '\n'.join([ gen_texts(
                                    words, links, macros, htmls,
                                    tc=5, pc=1, ec=2, lc=1, mc=1, hc=1, fc=0,
                                    nopipe=True
                                  )
                                  for j in range(randint(0,10)) ])
                      for i in range(10) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'textlines', t, testcount
            testcount += 1

    def test_7_bigtable( self ) :
        """Testing big tables"""
        print "\nTesting big tables"
        log.info( "Testing big tables" )
        testlist = [ '\n'.join([ gen_btableline( words, links, macros, htmls )
                                 for j in range(randint(0,10)) ]) +
                      gen_psep(randint(0,3)) for i in range(100) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'bigtable', t, testcount

    def test_8_table( self ) :
        """Testing tables"""
        print "\nTesting tables"
        log.info( "Testing tables" )
        testlist  = [ '\n'.join([ gen_row( words, links, macros, htmls )
                                  for j in range(randint(0,10)) ]) +
                      gen_psep(randint(0,3)) for i in range(100) ] 
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'table', t, testcount
            testcount += 1

    def test_9_ordlists( self ) :
        """\nTesting ordered list"""
        print "\nTesting ordered list"
        log.info( "Testing ordered list" )
        testlist  = [ '\n'.join([ gen_ordmark() + \
                                  gen_texts(
                                    words, links, macros, htmls,
                                    tc=5, pc=1, ec=2, lc=1, mc=1, hc=1, fc=1,
                                    nopipe=True
                                  )
                                  for j in range(randint(0,10)) ]) +
                      gen_psep(randint(0,3)) for i in range(100) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'ordlists', t, testcount
            testcount += 1

    def test_A_unordlists( self ) :
        """Testing unordered list"""
        print "\nTesting unordered list"
        log.info( "Testing unordered list" )
        testlist  = [ '\n'.join([ gen_unordmark() + \
                                  gen_texts(
                                    words, links, macros, htmls,
                                    tc=5, pc=1, ec=2, lc=1, mc=1, hc=1, fc=1,
                                    nopipe=True
                                  )
                                  for j in range(randint(0,10)) ]) +
                      gen_psep(randint(0,3)) for i in range(100) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'unordlists', t, testcount
            testcount += 1

    def test_B_blockquotes( self ) :
        """Testing blockquotes"""
        print "\nTesting blockquotes"
        log.info( "Testing blockquotes" )
        testlist  = [ '\n'.join([ gen_bqmark() + \
                                  gen_texts(
                                    words, links, macros, htmls,
                                    tc=5, pc=1, ec=2, lc=1, mc=1, hc=1, fc=1,
                                    nopipe=True
                                  )
                                  for j in range(randint(0,10)) ]) +
                      gen_psep(randint(0,3)) for i in range(100) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'blockquotes', t, testcount
            testcount += 1

    def test_C_definitions( self ) :
        """Testing definitions"""
        print "\nTesting definitions"
        log.info( "Testing definitions" )
        testlist  = [ '\n'.join([ gen_defnmark() + \
                                  gen_texts(
                                    words, links, macros, htmls,
                                    tc=5, pc=1, ec=2, lc=1, mc=1, hc=1, fc=1,
                                    nopipe=True
                                  )
                                  for j in range(randint(0,10)) ]) +
                      gen_psep(randint(0,3)) for i in range(100) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'definitions', t, testcount
            testcount += 1

    def test_D_unicode( self ) :
        """Testing unicoded test"""
        print "\nTesting unicoded text"
        log.info( "Testing unicoded text" )
        testlist = [ '' ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'unordlists', t, testcount
            testcount += 1

    def test_E_crooked_heading( self ) :
        """Testing crooked heading syntax"""
        print "\nTesting crooked heading syntax"
        log.info( "Testing crooked heading syntax" )
        testlist = [ crooked_heading ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'crooked_heading', t, testcount
            testcount += 1

    def test_E_crooked_wikix( self ) :
        """Testing crooked nowiki syntax"""
        print "\nTesting crooked nowiki syntax"
        log.info( "Testing crooked nowiki syntax" )
        testlist = [ crooked_nowiki, '{{{ \n hi world \n' ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'crooked_nowiki', t, testcount
            testcount += 1

    def test_F_crooked_table( self ) :
        """Testing crooked table syntax"""
        print "\nTesting crooked table syntax"
        log.info( "Testing crooked table syntax" )
        testlist  = [ crooked_table ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'crooked_table', t, testcount
            testcount += 1

    def test_G_crooked_btable( self ) :
        """Testing crooked big table syntax"""
        print "\nTesting crooked big table syntax"
        log.info( "Testing crooked big table syntax" )
        testlist = [ crooked_btable ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'crooked_btable', t, testcount
            testcount += 1

    def test_H_definitionwithnewline( self ) :
        """Testing definition item with new line"""
        print "\nTesting definition item with new line"
        log.info( "Testing crooked big table syntax" )
        testlist = [ definitionnewline ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'definitionnewline', t, testcount
            testcount += 1


