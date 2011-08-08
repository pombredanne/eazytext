# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

"""Module containing Node definition for all non-teminals and translator
functions for translating the text to HTML.

The AST tree is constructed according to the grammar. From the root
non-terminal use the children() method on every node to walk through the tree,
the only exceptions are,
  * `nowikilines` and `nowikicontent` rules are not available, in the AST
    tree.
  * `basictext`, though is a non-terminal with many alternative terminals,
  * does not differentiate it.

To walk throug the AST,
  * parse() the text, which returns the root non-terminal
  * Use children() method on every non-terminal node.
  * Use _terms and _nonterms attribute to get lists of terminals and
    non-terminals for every node.
"""

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   : None

import sys, re, copy
from   os.path          import basename, abspath, dirname, join, isdir, isfile

from   eazytext.style   import stylemarkup
from   eazytext.lib     import escape_htmlchars, obfuscatemail
from   eazytext.lexer   import ETLexer

templtdir = join( dirname(__file__), 'templates' )

class ASTError( Exception ):
    pass

class Context( object ):
    def __init__( self, htmlindent='' ):
        self.htmlindent = htmlindent

# ------------------- AST Nodes (Terminal and Non-Terminal) -------------------

class Node( object ):

    def __init__( self, parser ):
        self.parser = parser
        self.parent = None

    def children( self ):
        """Tuple of childrens in the same order as parsed by the grammar rule.
        """
        return tuple()

    def validate( self ):
        """Validate this node and all the children nodes. Expected to be called
        before processing the nodes."""
        pass

    def headpass1( self, igen ):
        """Pre-processing phase 1, useful to implement multi-pass compilers"""
        [ x.headpass1( igen ) for x in self.children() ]

    def headpass2( self, igen ):
        """Pre-processing phase 2, useful to implement multi-pass compilers"""
        [ x.headpass2( igen ) for x in self.children() ]

    def generate( self, igen, *args, **kwargs ):
        """Code generation phase. The result must be an executable python
        script"""
        [ x.generate( igen, *args, **kwargs ) for x in self.children() ]

    def tailpass( self, igen ):
        """Post-processing phase 1, useful to implement multi-pass compilers"""
        [ x.tailpass( igen ) for x in self.children() ]

    def dump( self, context ):
        """Simply dump the contents of this node and its children node and
        return the same."""
        return ''.join([ x.dump(context) for x in self.children() ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ):
        """ Pretty print the Node and all its attributes and children
        (recursively) to a buffer.
            
        buf:   
            Open IO buffer into which the Node is printed.
        
        offset: 
            Initial offset (amount of leading spaces) 
        
        attrnames:
            True if you want to see the attribute names in name=value pairs.
            False to only see the values.
        
        showcoord:
            Do you want the coordinates of each Node to be displayed.
        """

    #---- Helper methods

    def stackcompute( self, igen, compute, astext=True ):
        """Push a new buf, execute the compute function, pop the buffer and
        append that to the parent buffer."""
        igen.pushbuf()
        compute()
        igen.popcompute( astext=astext )
        return None

    def getroot( self ):
        """Get root node traversing backwards from this `self` node."""
        node = self
        parent = node.parent
        while parent : node, parent = parent, parent.parent
        return node

    def bubbleup( self, attrname, value ):
        """Bubble up value `value` to the root node and save that as its
        attribute `attrname`"""
        rootnode = self.getroot()
        setattr( rootnode, attrname, value )

    def bubbleupaccum( self, attrname, value, to=None ):
        """Same as bubbleup(), but instead of assigning the `value` to
        `attrname`, it is appended to the list."""
        rootnode = self.getroot()
        l = getattr( rootnode, attrname, [] )
        l.append( value )
        setattr( rootnode, attrname, l )

    @classmethod
    def setparent( cls, parnode, childnodes ):
        [ setattr( n, 'parent', parnode ) for n in childnodes ]


class Terminal( Node ) :
    """Abstract base class for EazyText AST terminal nodes."""

    def __init__( self, parser, terminal=u'', **kwargs ):
        Node.__init__( self, parser )
        self.terminal = terminal
        [ setattr( self, k, v ) for k,v in kwargs.items() ]

    def __repr__( self ):
        return unicode( self.terminal )

    def __str__( self ):
        return unicode( self.terminal )

    def generate( self, igen, *args, **kwargs ):
        """Dump the content."""
        igen.puttext( self.dump(None) )

    def dump( self, context ):
        """Simply dump the contents of this node and its children node and
        return the same."""
        return self.terminal

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ):
        """ Pretty print the Node and all its attributes and children
        (recursively) to a buffer.
            
        buf:   
            Open IO buffer into which the Node is printed.
        
        offset: 
            Initial offset (amount of leading spaces) 
        
        attrnames:
            True if you want to see the attribute names in name=value pairs.
            False to only see the values.
        
        showcoord:
            Do you want the coordinates of each Node to be displayed.
        """
        lead = ' ' * offset
        buf.write(lead + '<%s>: %r' % (self.__class__.__name__, self.terminal))
        buf.write('\n')


class NonTerminal( Node ):      # Non-terminal
    """Abstract base class for EazyText AST non-terminalnodes."""

    def __init__( self, *args, **kwargs ) :
        parser = args[0]
        Node.__init__( self, parser )
        self._terms, self._nonterms = tuple(), tuple()

    def flatten( self, attrnode, attrs ):
        """Instead of recursing through left-recursive grammar, flatten them
        into sequential list for looping on them later."""
        node, rclist = self, []

        if isinstance(attrs, basestring) :
            fn = lambda n : [ getattr(n, attrs) ]
        elif isinstance(attrs, (list,tuple)) :
            fn = lambda n : [ getattr(n, attr) for attr in attrs ]
        else :
            fn = attrs

        while node :
            rclist.extend( filter( None, list(fn(node))) )
            node = getattr(node, attrnode)
        rclist.reverse()
        return rclist



# ------------------- Non-terminal classes ------------------------

class WikiPage( NonTerminal ):
    """class to handle `wikipage` grammar."""
    tmpl_inclskin  = '<style type="text/css"> %s </style>'
    tmpl_article_o = '<article>'
    tmpl_article_c = '</article>'
    tmpl_html_o    = '<html><body>'
    tmpl_html_c    = '</body></html>'
    def __init__( self, parser, paragraphs ) :
        NonTerminal.__init__( self, parser, paragraphs )
        self._nonterms = (self.paragraphs,) = (paragraphs,)

    def children( self ) :
        return self._nonterms

    def generate( self, igen, *args, **kwargs ):
        etparser = self.parser.etparser
        etxconfig = etparser.etxconfig
        ashtml, nested = etxconfig['ashtml'], etxconfig['nested']
        # Use css skin
        if not nested and exconfig['include_skin'] :
            igen.puttext( self.tmpl_inclskin % etparser.skincss )
        # Wrapper Template
        (not nested and ashtml) and igen.puttext( self.tmpl_html_o )
        igen.puttext( self.tmpl_article_o )
        self.paragraphs.generate( igen, *args, **kwargs )
        igen.puttext( self.tmpl_article_c )
        (not nested and ashtml) and igen.puttext( self.tmpl_html_c )

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ):
        lead = ' ' * offset
        buf.write( lead + '-->wikipage: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+5, attrnames, showcoord) for x in self.children() ]


class Paragraphs( NonTerminal ) :
    """class to handle `paragraphs` grammar."""
    def __init__( self, parser, paras, para, ps ):
        NonTerminal.__init__( self, parser, paras, para, ps )
        self._nonterms = \
            (self.paragraphs, self.paragraph, self.paragraph_separator) = \
                paras, para, ps
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def headpass1( self, igen ):
        [ x.headpass1( igen ) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        [ x.generate( igen ) for x in self.flatten() ]

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self ):
        return ''.join([ x.dump() for x in self.flatten() ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        [ x.show(buf, offset, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        # Getch the attribute in reverse, so that when NonTerminal.flatten()
        # does a merged reverse it will in the correct order.
        return NonTerminal.flatten(
            self, 'paragraphs', ('paragraph_separator', 'paragraph')
        )


class Paragraph( NonTerminal ) :
    """class to handle `paragraph` grammar."""
    def __init__( self, parser, nonterm ) :
        NonTerminal.__init__( self, parser, nonterm )
        self._nonterms = (self.nonterm,) = (nonterm,)
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write(lead + 'paragraph: ')
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


#---- Nowiki

class NoWiki( NonTerminal ) :
    """class to handle `nowikiblock` grammar."""
    def __init__( self, parser, nwopen, nl, nwlines, nwclose, nl ):
        NonTerminal.__init__( self, parser, nwopen, nl, nwlines, nwclose, nl )
        self._terms = 
            self.NOWIKI_OPEN, self.NEWLINE1, self.NOWIKI_CLOSE, self.NEWLINE2 = \
                nwopen, nl, nwclose, nl
        self._terms = filter( None, self._terms )
        self._nonterms = (self.nwlines,) = (nwlines,)
        self.text = self.nwlines.dump( None )
        # Fetch the plugin
        try :
            headline = self.NOWIKI_OPEN.dump(None).strip()[3:].strip()
            self.nowikiname, xparams = headline.split(' ', 1)
            nowikiname = self.nowikiname.strip()
            extplugins = parser.etparser.etxconfig.get( 'extplugins', {} )
            factory = extplugins( nowikiname, None )
            self.extplugin = factory and factory( xparams.strip() )
            self.extplugin and self.extplugin.on_parse( self )
        except :
            if parser.etparser.debug : raise
            self.extplugin = None
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        x = ( self.NOWIKI_OPEN, self.NEWLINE1, self.nwline,s self.NOWIKI_CLOSE,
              self.NEWLINE2 )
        return filter( None, x )

    def headpass1( self, igen ):
        self.extplugin and self.extplugin.headpass1( self, igen )

    def headpass2( self, igen ):
        self.extplugin and self.extplugin.headpass2( self, igen )

    def generate( self, igen, *args, **kwargs ):
        self.extplugin and self.extplugin.generate( self, igen, *args, **kwargs )

    def tailpass( self, igen ):
        self.extplugin and self.extplugin.tailpass( self, igen )
    
    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'ext: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class NowikiLines( NonTerminal ):
    """class to handle `nowikilines` grammar."""
    def __init__( self, parser, nwlines, nowikitext, newline ) :
        NonTerminal.__init__( self, parser, nwlines, nowikitext, newline )
        self._terms = (self.NOWIKITEXT, self.NEWLINE) = nowikitext, newline
        self._nonterms = (self.nwlines,) = nwlines
        self._terms = filter( None, self._terms )
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return filter( None, (self.nwlines, self.NOWIKITEXT, self.NEWLINE) )

    def headpass1( self, igen ):
        raise Exception( 'Execution does not come to nowikilines' )

    def headpass2( self, igen ):
        raise Exception( 'Execution does not come to nowikilines' )

    def generate( self, igen, *args, **kwargs ):
        raise Exception( 'Execution does not come to nowikilines' )

    def tailpass( self, igen ):
        raise Exception( 'Execution does not come to nowikilines' )

    def dump( self ):
        return ''.join([ x.dump() for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write(lead + 'nowikilines: ')
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'nwlines', ('newline', 'nowikitext') )


#---- Heading

class Heading( NonTerminal ) :
    """class to handle `heading` grammar."""
    tmpl_o  = '<h%s class="etsec" style="%s">'
    tmpl_c  = '</h%s>\n'
    tmpl_a  = '<a id="%s"></a>'
    tmpl_ah = '<a class="etseclink" href="#%s" title="Link to this section">&#9875;</a>'

    def __init__( self, parser, heading, text_contents, newline ):
        NonTerminal.__init__( self, parser, heading, text_contents, newline )
        self._terms = self.HEADING, self.NEWLINE = heading, newline
        self._nonterms = (self.text_contents,) = (text_contents,)
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return filter( None, (self.HEADING, self.text_contents, self.NEWLINE) )

    def headpass1( self, igen ):
        igen.markupstack = []
        NonTerminal.headpass1( self, igen )

    def generate( self, igen, *args, **kwargs ):
        level, style = self.HEADING.level, stylemarkup( self.HEADING.style )
        igen.puttext( self.tmpl_o % (level, style) )
        text = self.text_contents.dump( None )
        self.text_contents.generate( igen, *args, **kwargs )
        igen.puttext( self.tmpl_a % self.text )
        igen.puttext( self.tmpl_ah % self.text )
        self.NEWLINE.generate( igen, *args, **kwargs )
        igen.puttext( self.tmpl_c % level )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'heading: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


#---- Horizontal rule

class HorizontalRule( Node ) :
    """class to handle `horizontalrule` grammar."""
    tmpl = '<hr class="ethorz"/>\n'
    def __init__( self, parser ) :
        NonTerminal.__init__( self, parser )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return tuple()

    def generate( self, igen, *args, **kwargs ):
        igen.puttext( self.tmpl )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'horizontalrule:' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


#---- Textlines

class TextLines( Node ) :
    """class to handle `textlines` grammar."""
    tmpl_o = '<p class="ettext">\n'
    tmpl_c = '</p>\n'

    def __init__( self, parser, textlines, textline ):
        NonTerminal.__init__( self, parser, textlines, textline )
        self._nonterms = self.textlines, self.textline = textlines, textline
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return filter( None, (self.textlines, self.textline) )

    def headpass1( self, igen ):
        [ x.headpass1( igen ) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        igen.puttext( tmpl_o )
        [ x.generate( igen ) for x in self.flatten() ]
        igen.puttext( tmpl_c )

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self ):
        return ''.join([ x.dump() for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'textlines: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'textlines', 'textline' )


class TextLine( Node ) :
    """class to handle `textline` grammar."""
    def __init__( self, parser, text_contents, newline ):
        NonTerminal.__init__( self, parser, text_contents, newline )
        self._nonterms = (self.text_contents,) = (text_contents,)
        self._terms = (self.NEWLINE,) = (self.newline,)
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return (self.text_contents, self.NEWLINE)

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'textline: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


#---- Big Table

class BTable( NonTerminal ) :
    """class to handle `btable` grammar."""
    def __init__( self, parser, btableblocks ):
        NonTerminal.__init__( self, parser, btableblocks )
        self._nonterms = (self.btableblocks,) = (btableblocks,)
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'btable: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        # Show children
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class BigtableBlocks( NonTerminal ) :
    """class to handle `btableblocks` grammar."""
    tmpl = {
      ETLexer.btopen  : ('<table class="etbtbl" style="%s">\n', None),
      ETLexer.btclose : ('</table>\n', None),
      ETLexer.btrow   : ('<tr class="etbtbl" style="%s">\n', '</tr>\n'),
      ETLexer.bthead  : ('<th class="etbtbl" style="%s">', '</th>\n'),
      ETLexer.btcell  : ('<td class="etbtbl" style="%s">', '</td>\n'),
    }
    def __init__( self, parser, btableblocks, btableblock ):
        NonTerminal.__init__( self, parser, btableblocks, btableblock )
        self._nonterms = self.btableblocks, self.btableblock = \
                btableblocks, btableblock
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def headpass1( self, igen ):
        [ x.headpass1( igen ) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        for bt in self.flatten() :
            style = stylemarkup( bt.style )
            tmpl_o, tmpl_c = self.tmpl.get( bt.btmark, (None, None) )
            tmpl_o and igen.puttext( tmpl_o % style )
            bt.generate( igen, *args, **kwargs )
            tmpl_c and igen.puttext( tmpl_c )

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self ):
        return ''.join([ x.dump() for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'btableblocks: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        # Show children
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'btableblocks', 'btableblock' )



class BigtableBlock( NonTerminal ) :
    """class to handle `bigtableblock` grammar."""
    def __init__( self, parser, btblock, btstart, text_contents, newline ):
        NonTerminal.__init__(
                self, parser, btblock, btstart, text_contents, newline )
        self._terms = self.BTABLE_START, self.NEWLINE = btstart, newline
        self._nonterms = self.bigtableblock, self.text_contents = \
                bigtableblock, text_contents
        self._terms = filter( None, self._terms )
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return filter(None, (self.BTABLE_START, self.text_contents, self.NEWLINE))

    def headpass1( self, igen ):
        igen.markupstack = []
        [ x.headpass1( igen ) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        [ x.generate( igen ) for x in self.flatten() ]

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self ):
        return ''.join([ x.dump() for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'bigtableblock: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        # Show children
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]

    def flatten( self ):
        return NonTerminal.flatten(
            self, 'bigtableblock', ('NEWLINE', 'text_contents')
        )

    btmark = property( lambda self : (self.BTABLE_START or self.bigtableblock).btmark )
    style = property( lambda self : (self.BTABLE_START or self.bigtableblock).style )


#---- Table

class Table( NonTerminal ) :
    """class to handle `table_rows` grammar."""
    tmpl_o = "<table>\n"
    tmpl_c = "</table>\n"
    def __init__( self, parser, table_rows ):
        NonTerminal.__init__( self, parser, table_rows )
        self._nonterms = (self.table_rows,) = (table_rows,)
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def generate( self, igen, *args, **kwargs ):
        igen.puttext( self.tmpl_o )
        NonTerminal.generate( self, igen, *args, **kwargs )
        igen.puttext( self.tmpl_c )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'table: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        # Show children
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class TableRows( NonTerminal ) :
    """class to handle `table_rows` grammar."""
    def __init__( self, parser, table_rows, table_rows ):
        NonTerminal.__init__( self, parser, table_rows, table_rows )
        self._nonterms = self.table_rows, self.table_rows = table_rows, table_rows
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def headpass1( self, igen ):
        [ x.headpass1( igen ) for x in self.flatten() ]
        igen.maxcolumns = max([ x.columns for x in self.flatten() ])

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        [ x.generate( igen ) for x in self.flatten() ]

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self ):
        return ''.join([ x.dump() for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'table_rows: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        # Show children
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'table_rows', 'table_rows' )


class TableRow( NonTerminal ) :
    """class to handle `table_row` grammar."""
    tmpl_o = '<tr class="ettbl">\n'
    tmpl_c = '</tr>\n'
    tmpl_emptyrow = '<td colspan="%s"></td>\n'
    def __init__( self, parser, tablecells, newline ):
        NonTerminal.__init__( self, parser, tablecells, newline )
        self._nonterms = (self.tablecells,) = (tablecells,)
        self._terms = (self.NEWLINE,) = (newline,)
        self.columns, self.emptyrow = None, None
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return (self.tablcells, self.NEWLINE)

    def headpass1( self, igen ):
        self.columns = len( self.tablecells.flatten() )
        NonTerminal.headpass1( self, igen )

    def headpass2( self, igen ):
        cell, colspan = None, 0
        for t in self.tablecells.flatten() :
            if t.colspan == 0 : colspan += 1
            else : t.colspan, cell, colspan = colspan, t, 0
        n = igen.maxcolumns - self.columns
        if cell and (colspan or n) :
            cell.colspan += colspan + n
        elif colspan or n :
            self.emptyrow = colspan + n

    def generate( self, igen, *args, **kwargs ):
        igen.puttext( self.tmpl_o )
        NonTerminal.generate( self, igen, *args, **kwargs )
        if self.emptyrows :
            igen.puttext( self.tmpl_emptyrow % self.emptyrows )
        igen.puttext( self.tmpl_c )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'table_row: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        # Show children
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class TableCells( NonTerminal ) :
    """class to handle `table_cells` grammar."""
    def __init__( self, parser, tablecells, tablecell ) :
        NonTerminal.__init__( self, parser, tablecells, tablecell )
        self._nonterms = self.tablecells, self.tablecell = tablecells, tablecell
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def headpass1( self, igen ):
        [ x.headpass1( igen ) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        [ x.generate( igen ) for x in self.flatten() ]

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self ):
        return ''.join([ x.dump() for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'table_cells: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'tablecells', 'tablecell' )


class TableCell( NonTerminal ) :
    """class to handle `table_cell` grammar."""
    RIGHTALIGN = '$'
    tmpl_o = { 'h' : '<th class="ettbl" colspan="%s" style="%s">',
               'd' : '<td class="ettbl" colspan="%s" style="%s">' }
    tmpl_c = { 'h' : '</th>\n', 'd' : '</td>\n' }
    style  = { RIGHTALIGN : 'text-align : right;' }

    def __init__( self, parser, cellstart, text_contents ) :
        NonTerminal.__init__( self, parser, markup, text_contents )
        self._terms = (self.TABLE_CELLSTART,) = (cellstart,)
        self._nonterms = (self.text_contents,) = (text_contents,)
        self._nonterms = filter( None, self._nonterms )
        self.colspan   = 1 if self.text_contents else 0
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return filter( None, self.TABLE_CELLSTART, self.text_contents )

    def headpass1( self, igen ):
        igen.markupstack = []
        NonTerminal.headpass1( self, igen )

    def generate( self, igen, *args, **kwargs ):
        if self.colspan > 0 :
            typ   = 'h' if self.TABLE_CELLSTART.ishead else 'd'
            cont  = self.text_contents.dump( None )
            style = stylemarkup( self.TABLE_CELLSTART.style ) + \
                    self.style.get( cont[-1], '' )
            igen.puttext( self.tmpl_o[typ] % (self.colspan, style) )
            self.text_contents.generate( igen, *args, **kwargs )
            igen.puttext( self.tmpl_c[typ] )
        elif self.text_contents :
            raise Exception( 'Table cell is not empty !' )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'table_cell: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


#---- Lists

class MixedLists( NonTerminal ) :
    """class to handle `mixedlists` grammar."""
    def __init__( self, parser, mixedlists, ulists, olists ) :
        NonTerminal.__init__( self, parser, mixedlists, ulists, olists )
        self._nonterms = self.mixedlists, self.ulists, self.olists = \
                mixedlists, ulists, olists
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def headpass1( self, igen ):
        [ x.headpass1( igen ) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        igen.lmarks.append( (None, 0) )
        [ x.generate( igen ) for x in self.flatten() ]

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self ):
        return ''.join([ x.dump() for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'mixedlists: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord), for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'mixedlists', ('ulists', 'olists') )


class Lists( NonTerminal ) :
    """class to handle `unorderedlists` or `unorderedlists` grammar."""
    tmpl_o = { 'ul' : '<ul class="et">', 'ol' : '<ol class="et">' }
    tmpl_c = { 'ul' : '</ul>', 'ol' : '</ol>' }
    def __init__( self, parser, lists, list_ ) :
        NonTerminal.__init__( self, parser, lists, list_ )
        self._nonterms = self.lists, self.list = lists, list_
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def headpass1( self, igen ):
        [ x.headpass1( igen ) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        for l in self.flatten() :
            level, type_ = igen.lmarks[-1]
            if l.level > level :
                for x in range(l.level-level) :
                    igen.puttext( self.tmpl_o[l.type] )
                    igen.lmarks.append( (l.level, l.type) )
            elif level < l.level :
                for x in range(level-l.level) :
                    level, type_ = igen.lmarks.pop(-1)
                    igen.puttext( self.tmpl_c[type_] )
            l.generate( igen, *args, **kwargs )

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self ):
        return ''.join([ x.dump() for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'lists: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'lists', 'list' )


class List( NonTerminal ) :
    """class to handle `orderedlist` or `unorderedlist` grammar."""
    tmpl_o = '<li class="et" style="%s">'
    tmpl_c = '</li>'
    def __init__( self, parser, lbegin, list_, text_contents, newline ):
        NonTerminal.__init__( self, parser, lbegin, list_, text_contents, newline )
        self._nonterms = \
            self.listbegin, self.list, self.text_contents, self.newline = \
                lbegin, list_, text_contents, newline
        self._terms = (self.NEWLINE,) = newline
        self._nonterms = filter( None, self._nonterms )
        self._terms = filter( None, self._terms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        x = (self.listbegin, self.list, self.text_contents, self.NEWLINE)
        return filter( None, x )

    def headpass1( self, igen ):
        igen.markupstack = []
        NonTerminal.headpass1( self, igen )

    def generate( self, igen, *args, **kwargs ):
        NonTerminal.generate( self, igen, *args, **kwargs )
        igen.puttext( self.tmpl_c ) if isinstance(self.parent, Lists) else None

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'list: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]

    level = property( lambda self : (self.lbegin or self.list).level )
    type  = property( lambda self : (self.lbegin or self.list).type )


class ListBegin( NonTerminal ) :
    """class to handle `unorderedlistbegin` or `unorderedlistbegin` grammar."""
    def __init__( self, parser, type_, lstart, text_contents, newline ) :
        NonTerminal.__init__( self, parser, type_, lstart, text_contents, newline )
        self.type, self.NEWLINE = type_, newline
        self.UNORDLIST_START, self.ORDLIST_START = \
            (lstart, None) if self.type == 'ul' else (None, lstart)
        self._terms = self.UNORDLIST_START, self.ORDLIST_START, self.NEWLINE
        self._nonterms = (self.text_contents,) = text_contents
        self._terms = filter( None, self._terms )
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        x = ( self.UNORDLIST_START, self.ORDLIST_START, self.text_contents, self.NEWLINE )
        return filter( None, x )

    def generate( self, igen, *args, **kwargs ):
        LIST = self.UNORDLIST_START or self.ORDLIST_START
        igen.puttext( self.parent.tmpl_o % stylemarkup( self.LIST.style ))
        self.text_contents.generate( igen, *args, **kwargs )
        self.newline.generate( igen, *args, **kwargs )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'listbegin: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]

    level = property(
        lambda self : (self.UNORDLIST_START or self.ORDLIST_START).level
    )


#---- Definitions

class Definitions( NonTerminal ) :
    """class to handle `definitionlists` grammar."""
    tmpl_o = '<dl class="et">\n'
    tmpl_c = '</dl>\n'
    def __init__( self, parser, defns=None, defn=None ) :
        NonTerminal.__init__( self, parser, defns, defn )
        self._nonterms = self.definitions, self.definition = defns, defn
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def headpass1( self, igen ):
        [ x.headpass1( igen ) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        igen.puttext( self.tmpl_o )
        [ x.generate( igen, *args, **kwargs ) for x in self.flatten() ]
        igen.puttext( self.tmpl_c )

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self ):
        return ''.join([ x.dump() for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'definitions: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'definitions', 'definition' )


class Definition( NonTerminal ) :
    """class to handle `definitionlist` grammar."""
    tmpl_dt = '<dt class="et"><b>%s</b></dt>\n'
    tmpl_dd_o = '<dd class="et">\n'
    tmpl_dd_c = '</dd>\n'
    def __init__( self, parser, defbegin, definition, text_contents, newline ):
        NonTerminal.__init__(
                self, parser, defbegin, definition, text_contents, newline )
        self._terms = (self.NEWLINE,) = (newline,)
        self._nonterms = (self.defbegin, self.definition, self.text_contents)
        self._terms = filter( None, self._terms )
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ):
        x = ( self.defbegin, self.definition, self.text_contents, self.newline )
        return filter( x, None )

    def headpass1( self, igen ):
        igen.markupstack = []
        NonTerminal.headpass1( self, igen )

    def generate( self, igen, *args, **kwargs ):
        NonTerminal.generate( self, igen, *args, **kwargs )
        igen.puttext( self.tmpl_dd_c ) if isinstance(self.parent, Definitions) else None

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'definition: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class DefinitionBegin( NonTerminal ) :
    """class to handle `definitionbegin` grammar."""
    def __init__( self, parser, defstart, text_contents, newline ) :
        NonTerminal.__init__( self, parser, defstart, text_contents, newline )
        self._terms = self.DEFINITION_START, self.NEWLINE = defstart, newline
        self._nonterms = (self.text_contents,) = (text_contents,)
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        x = (self.DEFINITION_START, self.text_contents, self.NEWLINE )
        return filter( None, x )

    def generate( self, igen, *args, **kwargs ):
        igen.puttext( self.parent.tmpl_dt % self.DEFINITION_START.defterm )
        igen.puttext( self.parent.tmpl_dd_o )
        self.text_contents.generate( igen, *args, **kwargs )
        self.newline.generate( igen, *args, **kwargs )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'definitionbegin: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


#---- Blockquotes

class BQuotes( NonTerminal ) :
    """class to handle `blockquotes` grammar."""
    tmpl_o = '<blockquote class="et %s">\n'
    tmpl_c = '</blockquote>\n'
    def __init__( self, parser, bquotes=None, bquote=None ) :
        NonTerminal.__init__( self, parser, bquotes, bquote )
        self._nonterms = self.bquotes, self.bquote = bquotes, bquote
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ):
        return self._nonterms

    def headpass1( self, igen ):
        level = 0
        for bquote in self.flatten() :
            if bquote.level != level :
                igen.markupstack = []
                continue
            bquote.headpass1( igen )

    def headpass2( self, igen ):
        [ x.headpass2(igen) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        igen.bqmarks = ['']
        [ bquote.generate( igen, *args, **kwargs ) for bquote in self.flatten() ]
        [ igen.puttext( self.tmpl_c ) for x in igen.bqmarks[-1] ]

    def tailpass( self, igen ):
        [ x.tailpass(igen) for x in self.flatten() ]

    def dump( self ):
        return ''.join([ x.dump() for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'bquotes: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'blockquotes', 'blockqoute' )


class BQuote( NonTerminal ) :
    """class to handle `blockquote` grammar."""
    def __init__( self, parser, bqstart, text_contents, newline ) :
        NonTerminal.__init__( self, parser, bqstart, text_contents, newline )
        self._terms = self.BQUOTE_START, self.NEWLINE = bqstart, newline
        self._nonterms = (self.text_contents,) = (text_contents,)
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ):
        x = (self.BQUOTE_START, self.text_contents, self.NEWLINE)
        return filter( None, x )

    def generate( self, igen, *args, **kwargs ):
        bqmark = self.BQUOTE_START.bqmark
        cls = 'firstlevel' if igen.bqmark[-1] == '' else 'innerlevel'
        if bqmark > igen.bqmarks[-1] :
            for x in bqmark.replace( igen.bqmarks[-1], '', 1 ) :
                igen.puttext( self.parent.tmpl_o % cls )
            igen.bqmarks.append( bqmark )
        elif bqmark < igen.bqmarks[-1] :
            for x in igen.bqmarks[-1].replace( bqmark, '', 1 ) :
                igen.puttext( self.parent.tmpl_c )
            igen.bqmarks.pop( -1 )
            igen.bqmarks.append( bqmark )
        self.text_contents.generate( igen, *args, **kwargs )
        self.newline.generate( igen, *args, **kwargs )

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'bquote: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]

    level  = property( lambda self : self.BQUOTE_START.level )


#---- Textcontents

class TextContents( NonTerminal ) :
    """class to handle `text_contents` grammar."""
    def __init__( self, parser, text_contents, text_content=None ) :
        NonTerminal.__init__( self, parser, text_contents, text_content )
        self._nonterms = (self.text_contents, self.text_content) = \
                text_contents, text_content
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def headpass1( self, igen ):
        [ x.headpass1(igen) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2(igen) for x in self.flatten() ]

    def generate( self, igen ):
        [ x.generate(igen) for x in self.flatten() ]

    def tailpass( self, igen ):
        [ x.tailpass(igen) for x in self.flatten() ]

    def dump( self ):
        return ''.join([ x.dump() for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        [ x.show(buf, offset, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'textcontents', 'text_content' )


class Link( NonTerminal ) :
    """class to handle `link` grammer.
    There are special links, 
        * - Open in new window,
        # - Create an anchor
        + - Image
    """
    prefixes     = '*#+><'
    l_template   = '<a class="etlink" target="%s" href="%s">%s</a>'
    a_template   = '<a id="%s" class="etlink anchor" name="%s">%s</a>'
    img_template = '<img class="et" src="%s" alt="%s" style="%s"/>'

    def __init__( self, parser, link ) :
        NonTerminal.__init__( self, parser, link )
        self._terms = (self.LINK,) = (link,)
        self.obfuscatemail = self.parser.etparser.etxconfig['obfuscatemail']
        self.html = self._parse( LINK.dump(None)[2:-2].lstrip() )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def _parse( self, _link ):
        prefix1, prefix2 = _link[:1], _link[1:2]
        _link = _link.lstrip( self.prefixes )
        try :
            href, text  = _link.split('|', 1)
        except :
            href, text = _link, _link
        href = escape_htmlchars( href.strip(' \t') )
        text = escape_htmlchars( text.strip(' \t') )

        if prefix1 == '*' :                         # Link - Open in new window
            html = self.l_template % ( '_blank', href, text )
        elif prefix1 == '#' :                       # Link - Anchor 
            html = self.a_template % ( href, text )
        elif prefix1 == '+' and prefix2 == '>' :    # Link - Image (right)
            html = self.img_template % ( href, text, 'float: right;' )
        elif prefix1 == '+' and prefix2 == '<' :    # Link - Image (left)
            html = self.img_template % ( href, text, 'float: left;' )
        elif prefix1 == '+' :                       # Link - Image
            html = self.img_template % ( href, text, '' )
        elif href[:6] == "mailto:" and self.obfuscatemail : # Link - E-mail
            if href == text :
                href = text = "mailto:" + obfuscatemail(href[7:])
            else :
                href = "mailto:" + obfuscatemail(href[7:])
            html = self.l_template % ( '', href, text )
        else :
            html = self.l_template % ( '', href, text )

        return html

    def children( self ) :
        return self._terms

    def generate( self, igen, *args, **kwargs ):
        igen.puttext( self.html )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'link: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class Macro( NonTerminal ) :
    """class to handle `macro` grammer."""
    def __init__( self, parser, macro ) :
        NonTerminal.__init__( self, parser, macro )
        self._terms = (self.MACRO,) = (macro,)
        # Fetch the plugin
        try :
            _macro = self.MACRO.dump(None)[2:-2]
            macroname, argstr = _macro.lstrip().split('(', 1)
            macroname = macroname.strip()
            argstr = argstr.rstrip(' \r)')
            macroplugins = parser.etparser.etxconfig.get( 'macroplugins', {} )
            factory = macroplugins.get( macroname, None )
            self.macroplugin = factory and factory( argstr.strip() )
            self.macroplugin.on_parse( self )
        except :
            if parser.etparser.debug : raise
            self.macroplugin = None
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ):
        return self._terms

    def headpass1( self, igen ):
        self.macroplugin and self.macroplugin.headpass1( self, igen )

    def headpass2( self, igen ):
        self.macroplugin and self.macroplugin.headpass2( self, igen )

    def generate( self, igen, *args, **kwargs ):
        self.macroplugin and self.macroplugin.generate( self, igen, *args, **kwargs )

    def tailpass( self, igen ):
        self.macroplugin and self.macroplugin.tailpass( self, igen )
    
    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'macro: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class Html( NonTerminal ) :
    """class to handle `html` grammer."""
    def __init__( self, parser, html ) :
        NonTerminal.__init__( self, parser, html )
        self._terms = (self.HTML,) = (html,)
        # Fetch the plugin
        self.tagname, self.text = html.dump(None)[2:-2].split(' ',1)
        self.tagname = self.tagname.strip()
        ttplugins = parser.etparser.etxconfig.get( 'ttplugins', {} )
        self.ttplugin = tagplugins.get( self.tagname, None )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ):
        return self._terms

    def headpass1( self, igen ):
        self.ttplugin and self.ttplugin.headpass1( self, igen )

    def headpass2( self, igen ):
        self.ttplugin and self.ttplugin.headpass2( self, igen )

    def generate( self, igen, *args, **kwargs ):
        self.ttplugin and self.ttplugin.generate( self, igen, *args, **kwargs )

    def tailpass( self, igen ):
        self.ttplugin and self.ttplugin.tailpass( self, igen )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'html: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class BasicText( NonTerminal ) :
    """class to handle `basictext` grammar."""
    def __init__( self, parser, term ) :
        NonTerminal.__init__( self, parser, term )
        self._term = (self.TERMINAL,) = (term,)
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._terms

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write(lead + 'basictext: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class MarkupText( NonTerminal ) :
    """class to handle `markuptext` grammar."""
    def __init__( self, parser, term ) :
        NonTerminal.__init__( self, parser, term )
        self._term = (self.TERMINAL,) = (term,)
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._terms

    def headpass1( self, igen ):
        TERM = self.TERMINAL
        OPEN = igen.markupstack and igen.markupstack[-1].TERMINAL
        if OPEN.markup == TERM.markup :
            OPEN.html, TERM.html = \
                    OPEN.tmpl_o % stylemarkup(OPEN.style), TERM.tmpl_c
        else :
            igen.markupstack.append( self )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write(lead + 'markuptext: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class ParagraphSeparator( NonTerminal ) :
    """class to handle `paragraph_separator` grammar."""

    def __init__( self, parser, ps, newline ) :
        NonTerminal.__init__( self, parser, ps, newline )
        self.newline = self.empty = self.paragraph_separator = None
        self._terms = (self.NEWLINE,) = (newline,)
        self._nonterms = (self.paragraph_separator,) = (ps,)
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return filter( None, (self._nonterms+self._terms) )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        pass



#-------------------------- AST Terminals -------------------------

class BASICTEXT( object ):
    def generate( self, igen, *args, **kwargs ):
        igen.puttext( self.html )

class MARKUPTEXT( object ):
    html, spatt = '', re.compile( ETLexer.style )
    def generate( self, igen, *args, **kwargs ):
        igen.puttext( self.html or self.terminal )
    def _style( self ):
        rc = self.spatt.findall( self.terminal )
        return rc[0][1:-1] if rc else ''
    style  = property( lambda self : self._style() )

#---- Text
class NEWLINE( Terminal ): pass
class ESCAPED_TEXT( Terminal ):
    html   = property( lambda self : self.terminal )
class TEXT( Terminal, BASICTEXT ):
    html   = property( lambda self : self.terminal )
class SPECIALCHAR( Terminal, BASICTEXT ):
    html   = property( lambda self : self.terminal )
class HTTP_URI( Terminal, BASICTEXT ):
    tmpl   = '<a class="ethttpuri" href="%s">%s</a>'
    html   = property( lambda self : self.tmpl % (self.terminal, self.terminal) )
class HTTPS_URI( Terminal, BASICTEXT ):
    tmpl   = '<a class="ethttpsuri" href="%s">%s</a>'
    html   = property( lambda self : self.tmpl % (self.terminal, self.terminal) )
class WWW_URI( Terminal, BASICTEXT ):
    tmpl   = '<a class="etwwwuri" href="%s">%s</a>'
    html   = property( lambda self : self.tmpl % (self.terminal, self.terminal) )

#---- Text markup
class M_SPAN( Terminal, MARKUPTEXT ):
    markup = 'span'
    tmpl_o = '<span class="etmark" style="%s">'
    tmpl_c = '</span>'

class M_BOLD( Terminal, MARKUPTEXT ):
    markup = 'bold'
    tmpl_o = '<strong class="etmark" style="%s">'
    tmpl_c = '</strong>'

class M_ITALIC( Terminal, MARKUPTEXT ):
    markup = 'italic'
    tmpl_o = '<em class="etmark" style="%s">'
    tmpl_c = '</em>'

class M_UNDERLINE( Terminal, MARKUPTEXT ):
    markup = 'underline'
    tmpl_o = '<u class="etmark" style="%s">'
    tmpl_c = '</u>'

class M_SUPERSCRIPT( Terminal, MARKUPTEXT ):
    markup = 'superscript'
    tmpl_o = '<sup class="etmark" style="%s">'
    tmpl_c = '</sup>'

class M_SUBSCRIPT( Terminal, MARKUPTEXT ):
    markup = 'subscript'
    tmpl_o = '<sub class="etmark" style="%s">'
    tmpl_c = '</sub>'

class M_BOLDITALIC( Terminal, MARKUPTEXT ):
    markup = 'bolditalic'
    tmpl_o = '<strong><em class="etmark" style="%s">'
    tmpl_c = '</em></strong>'

class M_BOLDUNDERLINE( Terminal, MARKUPTEXT ):
    markup = 'boldunderline'
    tmpl_o = '<strong><u class="etmark" style="%s">'
    tmpl_c = '</u></strong>'

class M_ITALICUNDERLINE( Terminal, MARKUPTEXT ):
    markup = 'italicunderline'
    tmpl_o = '<em><u class="etmark" style="%s">'
    tmpl_c = '</u></em>'

class M_BOLDITALICUNDERLINE( Terminal, MARKUPTEXT ):
    markup = 'bolditalicunderline'
    tmpl_o = '<strong><em><u class="etmark" style="%s">'
    tmpl_c = '</u></em></strong>'

#---- Inline text blocks
class LINK( Terminal ): pass
class NESTEDLINK( Terminal ): pass
class MACRO( Terminal ): pass
class HTML( Terminal ): pass

#---- Text Blocks
class HORIZONTALRULE( Terminal ): pass
class HEADING( Terminal ):
    hpatt1 = re.compile( r'={1,6}' ) 
    hpatt2 = re.compile( r'[hH][123456]' )
    spatt  = re.compile( ETLexer.style )
    def _level( self ):
        x = self.hpatt1.findall( self.terminal.strip() )
        y = x or self.hpatt2.findall( self.terminal.strip() )
        try    : level = len(x[0]) if x else int(y[1])
        except : level = 6
        return level
    def _style( self ):
        rc = self.spatt.findall( self.terminal.strip() )
        return rc[0][1:-1] if rc else ''
    level  = property( lambda self : self._level() )
    style  = property( lambda self : self._style() )

class ORDLIST_START( Terminal ):
    spatt = re.compile( ETLexer.style )
    def _style( self ):
        rc = self.spatt.findall( self.terminal.strip() )
        return rc[0][1:-1] if rc else ''
    lmark = property( lambda self : self.spatt.sub( '', self.terminal.strip() ).strip() )
    level = property( lambda self : len(self.lmark) )
    style = property( lambda self : self._style() )

class UNORDLIST_START( Terminal ):
    spatt = re.compile( ETLexer.style )
    def _style( self ):
        rc = self.spatt.findall( self.terminal.strip() )
        return rc[0][1:-1] if rc else ''
    lmark = property( lambda self : self.spatt.sub('', self.terminal.strip()).strip() )
    level = property( lambda self : len(self.lmark) )
    style = property( lambda self : self._style() )

class DEFINITION_START( Terminal ):
    defterm = property( lambda self : self.terminal.strip()[1:-2] )

class BQUOTE_START( Terminal ) :
    bqmark = property( lambda self : self.terminal.strip() )
    level  = property( lambda self : len(self.bqmark) )

class BTABLE_START( Terminal ): pass
    spatt = re.compile( ETLexer.style )
    def _style( self ):
        rc = self.spatt.findall( self.terminal.strip() )
        return rc[0][1:-1] if rc else ''
    btmark = property( lambda self : self.terminal.strip()[:3] )
    style  = property( lambda self : self._style() )

class TABLE_CELLSTART( Terminal ): pass
    spatt = re.compile( ETLexer.style )
    def _style( self ):
        rc = self.spatt.findall( self.terminal.strip() )
        return rc[0][1:-1] if rc else ''
    ishead = property( lambda self : '=' in self.terminal.strip()[:2] )
    style  = property( lambda self : self._style() )

class NOWIKI_OPEN( Terminal ): pass
class NOWIKITEXT( Terminal ): pass
class NOWIKI_CLOSE( Terminal )  pass
#---- Endmarker
class ENDMARKER( Terminal ): pass
