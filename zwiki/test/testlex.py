import unittest
import os

from   nose.tools       import assert_equal

from   zwiki.zwlexer    import ZWLexer

stdfiles_dir    = os.path.join( os.path.split( __file__ )[0], 'stdfiles' )
rndfiles_dir    = os.path.join( os.path.split( __file__ )[0], 'rndfiles' )
samplefiles_dir = os.path.join( os.path.split( __file__ )[0], 'samplefiles' )
zwlex           = None

stdfiles        = [ 'creole1.0test.txt' ]

_formatlines    = lambda ptext : [ '    ' + ptext[i:120]
                                        for i in range( 0, len(ptext), 120 ) ]

def setUpModule() :
    global zwlex
    zwlex = ZWLexer()
    zwlex.build()

def tearDownModule() :
    pass


class TestLex( unittest.TestCase ) :
    """Test cases to validate ZWiki lexer."""

    def _print_tokens( self, text ) :
        zwlex.input( text )
        print "List of tokens ..."
        while 1:
            tok = zwlex.token()
            if not tok: break
            print tok.type, tok.lineno, zwlex.filename, tok.lexpos
            if tok.type != 'NEWLINE' :
                for t in _formatlines( tok.value ) :
                    print t

    def test_stdfiles( self ) :
        for file in stdfiles :
            text = open( os.path.join( stdfiles_dir, file )).read()
            self._print_tokens( text )
