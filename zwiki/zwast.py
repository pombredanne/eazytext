"""Module containing the Nodes for all non-teminals"""

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   :
#   1. Add unicode support
#   2. Add ismatched() method.
#   3. For links that open in new window, append a character that would say
#      so.

import sys
import re
import cElementTree       as et

from   zwiki.macro        import build_macro
from   zwiki.zwext        import build_zwext
from   zwiki              import escape_htmlchars, split_style, obfuscatemail
from   zwiki.textlexer    import TextLexer
from   zwiki.stylelookup  import *
import zwiki.ttags        as tt

# text type for BasicText
TEXT_ZWCHARPIPE     = 'zwcharpipe'
TEXT_ALPHANUM       = 'alphanum'
TEXT_SPECIALCHAR    = 'specialchar'
TEXT_SPECIALCHAR_LB = 'linebreak'
TEXT_HTTPURI        = 'httpuri'
TEXT_WWWURI         = 'wwwuri'
TEXT_ESCAPED        = 'escaped'
TEXT_LINK           = 'link'
TEXT_MACRO          = 'macro'
TEXT_HTML           = 'html'
TEXT_NEWLINE        = 'newline'

TEXT_M_SPAN              = 'm_span'
TEXT_M_BOLD              = 'm_bold'
TEXT_M_ITALIC            = 'm_italic'
TEXT_M_UNDERLINE         = 'm_underline'
TEXT_M_SUBSCRIPT         = 'm_subscript'
TEXT_M_SUPERSCRIPT       = 'm_superscript'
TEXT_M_BOLDITALIC        = 'm_bolditalic'
TEXT_M_BOLDUNDERLINE     = 'm_boldunderline'
TEXT_M_ITALICUNDERLINE   = 'm_italicunderline'
TEXT_M_BOLDITALICUNDERLINE = 'm_bolditalicunderline'

# List Type
LIST_ORDERED        = 'ordered'
LIST_UNORDERED      = 'unordered'

# Markup
M_PIPE              = '|'
M_PIPEHEAD          = '|='

FORMAT_NON          = 'fmt_non'
FORMAT_EMPTY        = 'fmt_empty'
FORMAT_BTABLE       = 'fmt_bt'
FORMAT_BTABLESTYLE  = 'fmt_btstyle'

# ---------------------- Helper Class objects --------------

def style_color( m ) :
    return 'color: %s;' % fgcolors[m]

def style_background( m ) :
    return 'background: %s;' % bgcolors[m]

def style_border( m ) :
    w, style, color = m[1:].split( ',' )
    color = fgcolors[color]
    return 'border : %spx %s %s;' % ( w, style, color )

def style_margin( m ) :
    return 'margin : %spx' % m[:-1]

def style_padding( m ) :
    return 'padding : %spx' % m[1:]

fg_pattern      = ( re.compile( r'^[a-z]$' ), style_color )
bg_pattern      = ( re.compile( r'^[A-Z]$' ), style_background )
border_pattern  = ( re.compile( r'^/[0-9]+,(dotted|dashed|solid|double|groove|ridge|inset|outset),[a-z]$' ),
                    style_border 
                  )
margin_pattern  = ( re.compile( r'^[0-9]+\|$' ), style_margin )
padding_pattern = ( re.compile( r'^\|[0-9]+$' ), style_padding )

stylematcher    = [ fg_pattern, bg_pattern, border_pattern, margin_pattern,
                    padding_pattern ]

def styleparser( stylemarkups ) :
    """Parse the text for style markup and convert them into html style
    attribute values"""
    stylemarkups = stylemarkups.strip('{}')
    props        = [ prop.strip( ' \t' ) for prop in stylemarkups.split( ';' ) ]
    styleprops   = []
    for prop in props :
        for regex, func in stylematcher :
            if regex.match( prop ) :
                styleprops.append( func( prop ))
                break
        else :
            styleprops.append( prop )
    return '; '.join( styleprops )


def markup2html( type, mtext, steed ) :
    if type == TEXT_M_SPAN :
        
        tags = [ '<span style="%s">' % styleparser( mtext[2:] ), '</span>' ]

    elif type == TEXT_M_BOLD :

        tags = [ '<strong style="%s">' % styleparser( mtext[2:] ), '</strong>' ]

    elif type == TEXT_M_ITALIC :

        tags = [ '<em style="%s">' % styleparser( mtext[2:] ), '</em>' ]

    elif type == TEXT_M_UNDERLINE :

        tags = [ '<u style="%s">' % styleparser( mtext[2:] ), '</u>' ]

    elif type == TEXT_M_SUPERSCRIPT :

        tags = ['<sup style="%s">' % styleparser( mtext[2:] ), '</sup>' ]

    elif type == TEXT_M_SUBSCRIPT :

        tags = [ '<sub style="%s">' % styleparser( mtext[2:] ), '</sub>' ]

    elif type == TEXT_M_BOLDITALIC :

        tags = [ '<strong style="%s"><em>' % styleparser( mtext[2:] ), '</em></strong>']

    elif type == TEXT_M_BOLDUNDERLINE :

        tags = [ '<strong style="%s"><u>' % styleparser( mtext[2:] ), '</u></strong>' ]

    elif type == TEXT_M_ITALICUNDERLINE :

        tags = [ '<em style="%s"><u>' % styleparser( mtext[2:] ), '</u></em>' ]

    elif type == TEXT_M_BOLDITALICUNDERLINE :

        tags = [ '<strong style="%s"><em><u>' % styleparser( mtext[3:] ),
                 '</u></em></strong>' ]

    return tags[steed]


class Content( object ) :
    """The whole of wiki text is parsed and encapulated as lists of Content
    objects."""
    def __init__( self, parser, text, type=None, html=None ) :
        self.parser = parser
        self.text   = text
        self.type   = type
        self.html   = html

    def __repr__( self ) :
        return "Content<'%s','%s','%s'>" % (self.text, self.type, self.html )

def process_textcontent( contents ) :
    """From the list of content objects (tokenized), construct the html page."""
    count = len(contents)
    for i in range( count ) :
        beginmarkup_cont = contents[i]
        if beginmarkup_cont.html or \
           beginmarkup_cont.type == TEXT_SPECIALCHAR or\
           beginmarkup_cont.type == TEXT_ALPHANUM :
            continue
        for j in range( i+1, count ) :
            endmarkup_cont = contents[j]
            if endmarkup_cont.type == beginmarkup_cont.type and j != i+1  :
                # Found the markup pair, with some text in between
                beginmarkup_cont.html = markup2html( beginmarkup_cont.type,
                                                     beginmarkup_cont.text,
                                                     0
                                                   )
                endmarkup_cont.html   = markup2html( endmarkup_cont.type,
                                                     endmarkup_cont.text,
                                                     1
                                                   )
                # All the markups in between should be self contained between
                # i and j
                process_textcontent( contents[i+1:j] )
                break;
        else :
            beginmarkup_cont.html = beginmarkup_cont.text

    return

#def parse_text( parser, text ) :
#    """Parse the text for wiki text markup and valid text content and return a
#    list of content object"""
#
#    def errfoo(msg, a, b):
#        print msg
#
#    textlex = TextLexer( errfoo )
#    textlex.build()
#    if text :
#        textlex.input( text )
#        tok = textlex.token()
#        contents = []
#        while tok :
#            if tok.type == 'M_TEXT' :
#                cont = Content( parser, tok.value, TEXT_ALPHANUM, 
#                                escape_htmlchars( tok.value )
#                              )
#            elif tok.type == 'M_SPCHAR' :
#                cont = Content( parser, tok.value, TEXT_SPECIALCHAR, 
#                                escape_htmlchars( tok.value )
#                              )
#            else :
#                cont = Content( parser, tok.value, tok.type )
#
#            contents.append( cont )
#            tok = textlex.token()
#
#    return contents

# ---------------------- Exception classes ----------------

class ZWASTError( Exception ):
    pass


# ---------------------- AST class nodes -------------------

class Node( object ):
    """Abstract base class for ZWiki AST nodes. DO NOT instanciate."""

    def children( self ):
        """A sequence of all children that are Nodes"""
        pass

    def tohtml( self ):
        """Translate the node and all the children nodes to html markup and
        return the content"""

    def ismatched( self ) :
        """This interface should return a boolean indicating whether the html
        generated by this node is matched. If a node expects that the html
        might be mismatched"""
        return True

    def dump( self ):
        """Simply dump the contents of this node and its children node and
        return the same."""

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ):
        """ Pretty print the Node and all its attributes and children
        (recursively) to a buffer.
            
        file:   
            Open IO buffer into which the Node is printed.
        
        offset: 
            Initial offset (amount of leading spaces) 
        
        attrnames:
            True if you want to see the attribute names in name=value pairs.
            False to only see the values.
        
        showcoord:
            Do you want the coordinates of each Node to be displayed."""
        pass


class Wikipage( Node ):
    """class to handle `wikipage` grammar."""

    def __init__( self, parser, paragraphs ) :
        self.parser     = parser
        self.paragraphs = paragraphs

    def children( self ) :
        return (self.paragraphs,)

    def tohtml( self ):
        zwparser = self.parser.zwparser
        # Call the registered prehtml methods.
        zwparser.onprehtml_macro()
        zwparser.onprehtml_zwext()
        
        html  = ''.join([ c.tohtml() for c in self.children() ])
        # Since this is the Root node for all the other nodes, the converted
        # HTML string is stored in the parser object.
        style = '; '.join([ k + ' : ' + zwparser.wiki_css[k]
                            for k in zwparser.wiki_css ])
        style += '; ' + zwparser.style + '; '
        zwparser.html = '<div style="' + style + '">' + html + '</div>'

        # Call the registered posthtml method.
        zwparser.onposthtml_macro()
        zwparser.onposthtml_zwext()

        # Collect, prepend and append `posthtml`s from macros and extensions
        objs = [ o for o in zwparser.macroobjects + zwparser.zwextobjects
                   if getattr( o, 'posthtml', None ) and
                   getattr( o, 'postindex', None ) ]
        peerhtml_neg = ''
        peerhtml_pos = ''
        for o in sorted( objs, key=lambda x : x.postindex ) :
            if o.postindex < 0 :
                peerhtml_neg += o.posthtml
            elif o.postindex > 0 :
                peerhtml_pos += o.posthtml

        # Final html
        zwparser.html = '<div class="wikiblk">' + \
                        peerhtml_neg + zwparser.html + peerhtml_pos + '</div>'
        return zwparser.html

    def dump( self ) :
        return ''.join([ c.dump() for c in self.children() ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'wikipage: ' )

        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        for c in self.children():
            c.show( buf, offset + 2, attrnames, showcoord )


class Paragraphs( Node ) :
    """class to handle `paragraphs` grammar."""

    def __init__( self, parser, *args  ) :
        self.parser = parser
        if len( args ) == 1 :
            self.paragraph_separator = args[0]
        elif len( args ) == 2 :
            self.paragraph           = args[0]
            self.paragraph_separator = args[1]
        elif len( args ) == 3 :
            self.paragraphs          = args[0]
            self.paragraph           = args[1]
            self.paragraph_separator = args[2]

    def children( self ) :
        childnames = [ 'paragraphs', 'paragraph', 'paragraph_separator' ]
        nodes      = filter(
                        None,
                        [ getattr( self, attr, None ) for attr in childnames ]
                     )
        return tuple(nodes)

    def tohtml( self ):
        return ''.join([ c.tohtml() for c in self.children() ])

    def dump( self ) :
        return ''.join([ c.dump() for c in self.children() ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'paragraphs: ' )

        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        for c in self.children():
            c.show( buf, offset + 2, attrnames, showcoord )


class Paragraph( Node ) :
    """class to handle `paragraph` grammar."""

    def __init__( self, parser, paragraph ) :
        self.parser = parser
        self.paragraph = paragraph

    def children( self ) :
        return ( self.paragraph, )

    def tohtml( self ):
        html = self.paragraph.tohtml()
        # Before packging into a paragraph element check whether the html is
        # correctly formed.
        try : 
            et.fromstring( '<div>' + html + '</div>' )
        except :
            if self.parser.zwparser.debug :
                raise
        else :
            html = '<p>' + html + '</p>'
        return html

    def dump( self ) :
        return self.paragraph.dump()

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write(lead + 'paragraph: ')

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        for c in self.children() :
            c.show( buf, offset + 2, attrnames, showcoord )


class NoWiki( Node ) :
    """class to handle `nowikiblock` grammar."""

    def __init__( self, parser, opennowiki, opennl, nowikilines,
                  closenowiki=None, closenl=None, skip=False  ) :
        self.parser      = parser
        self.xparams     = map( lambda x : x.strip(' \t'),
                                opennowiki[3:].strip( ' \t' ).split(' ')
                              )
        self.xwikiname   = self.xparams and self.xparams.pop(0) or ''
        self.opennewline = Newline( parser, opennl )
        self.nowikilines = nowikilines
        self.skip        = skip
        if self.skip :
            self.nowikitext   = opennowiki  + opennl + nowikilines
        else :
            self.closenewline = Newline( parser, closenl )
            self.wikixobject  = build_zwext( self, nowikilines )
            self.nowikitext   = opennowiki  + opennl + nowikilines + \
                                closenowiki + closenl

    def children( self ) :
        return (self.nowikilines,)

    def tohtml( self ):
        if self.skip :
            return ''
        else :
            return self.wikixobject.tohtml()

    def dump( self ) :
        return self.nowikitext

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'nowikiblock: `%s` ' % self.nowikilines.split('\n')[0] )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')


class Heading( Node ) :
    """class to handle `heading` grammar."""

    def _parseheadmarkup( self, headmarkup ) :
        """Convert the header markup into respective level. Note that, header
        markup can be specified with as ={1,5} or h[1,2,3,,4,5]"""
        headmarkup = headmarkup.lstrip( ' \t' )

        off = headmarkup.find( '{' )
        if off > 0 :
            style      = styleparser( headmarkup[off:] )
            headmarkup = headmarkup[:off]
        else :
            headmarkup = headmarkup
            style      = ''

        if '=' in headmarkup :
            level = len(headmarkup)
        elif headmarkup[0] in 'hH' :
            level = int(headmarkup[1])
        else :
            level = 5
        return headmarkup, level, style

    def __init__( self, parser, headmarkup, headline, newline ) :
        self.headmarkuptxt = headmarkup
        self.headmarkup, self.level, self.style = self._parseheadmarkup( headmarkup )
        self.parser       = parser
        self.textcontents = headline
        self.newline      = Newline( parser, newline )

    def children( self ) :
        return ( self.headmarkup, self.textcontents, self.newline )

    def tohtml( self ):
        l    = self.level
        contents = []
        [ contents.extend( item.contents )
          for item in self.textcontents.textcontents ]
        process_textcontent( contents )
        text = self.textcontents.dump().strip(' \t=')
        html = self.textcontents.tohtml().strip(' \t=')
        html = '<h%s style="%s"><a style="visibility : hidden;" name="%s"></a>%s</h%s>' % \
                        ( l, self.style, text, html, l ) + \
               self.newline.tohtml()
        return html

    def dump( self ) :
        return self.headmarkuptxt + self.textcontents.dump() + self.newline.dump()

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'heading: `%s` ' % self.children()[:-1] )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        self.newline.show( buf, offset + 2, attrnames, showcoord )


class HorizontalRule( Node ) :
    """class to handle `horizontalrule` grammar."""

    def __init__( self, parser, hrule, newline ) :
        self.parser = parser
        self.hrule   = hrule
        self.newline = Newline( parser, newline )

    def children( self ) :
        return (self.hrule, self.newline)

    def tohtml( self ):
        return '<hr></hr>'

    def dump( self ) :
        return self.hrule + self.newline.dump()

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'horizontalrule:' )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        self.newline.show( buf, offset + 2, attrnames, showcoord )


class TextLines( Node ) :
    """class to handle `textlines` grammar."""

    def __init__( self, parser, textcontents, newline  ) :
        self.parser = parser
        self.textlines = [ (textcontents, Newline( parser, newline )) ]

    def appendline( self, textcontents, newline ) :
        self.textlines.append( (textcontents, Newline( self.parser, newline )) )

    def children( self ) :
        return (self.textlines,)

    def tohtml( self ) :
        # Combine text lines, process the text contents and convert them into
        # html
        contents = []
        [ contents.extend( item.contents )
          for textcontents, nl in self.textlines 
          for item in textcontents.textcontents ]
        process_textcontent( contents )
        html   = ''
        for textcontents, newline in self.textlines :
            html += textcontents.tohtml()
            html += newline.tohtml()
        return html

    def dump( self ) :
        txt = ''.join([ ''.join([ item.dump()
                                  for item in textcontents.textcontents ]) +\
                        newline.dump()
                        for textcontents, newline in self.textlines ])
        return txt

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'textlines: ' )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        linecount = 1
        for textcontent, newline in self.textlines :
            buf.write( lead + '(line %s)\n' % linecount )
            linecount += 1
            textcontent.show( buf, offset + 2, attrnames, showcoord )
            newline.show( buf, offset + 2, attrnames, showcoord )


class BtableRows( Node ) :
    """class to handle `btablerows` grammar"""

    def __init__( self, parser, row ) :
        self.parser = parser
        self.rows   = [ row ]

    def appendrow( self, row ) :
        self.rows.append( row )

    def children( self ) :
        return self.rows

    def tohtml( self ) :
        html       = ''
        closerow   = []       # Stack to manage rows
        closetable = []       # Stack to manage table
        for row in self.rows :
            mrkup = row.rowmarkup.lstrip( ' \t' )[:3]
            style = row.style()
            if mrkup == '||{' : # open table
                if closetable : continue
                style       = 'border-left : 1px solid gray; ' + \
                              'border-top : 1px solid gray; ' + style
                html  += '<table cellspacing="0px" cellpadding="5px" style="%s">' % \
                            ( style )
                closetable.append( '</table>' )
            elif mrkup == '||-' : # Row
                if closerow :
                    html += closerow.pop()
                html += '<tr style="%s">' % style
                closerow.append( '</tr>' )
            elif mrkup == '||=' : # header cell
                style = 'padding : 5px; border-right : 1px solid gray; ' + \
                        'border-bottom : 1px solid gray; ' + style
                html += '<th style="%s">%s</th>' % (style, row.tohtml())
            elif mrkup == '|| ' : # Cell
                style = 'padding : 5px; border-right : 1px solid gray; ' + \
                        'border-bottom : 1px solid gray; ' + style
                html += '<td style="%s">%s</td>' % (style, row.tohtml())
            elif mrkup == '||}' : # close table
                pass

        if closerow :
            html+= ''.join([ closerow.pop() for i in range(len(closerow)) ])
        if closetable :
            html+= ''.join([ closetable.pop() for i in range(len(closetable)) ])
        return html

    def dump( self ) :
        return ''.join([ row.dump() for row in self.rows ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        if showcoord :
            buf.write( ' (at %s)' % self.coord )

        for row in self.rows :
            row.show( buf, offset + 2, attrnames, showcoord )


class BtableRow( Node ) :
    """class to handle `btablerow` grammar"""

    def __init__( self, parser, rowmarkup, rowitem, newline, type=None ) :
        self.parser    = parser
        self.rowtype   = type
        self.rowmarkup = rowmarkup
        if isinstance( rowitem, Empty ) :
            self.empty        = rowitem
            self.textcontents = None
        elif isinstance( rowitem, TextContents ) :
            self.textcontents = rowitem
            self.empty        = None
        else :
            raise ZWASTError( "Unknown `rowitem` for BtableRow() node" )
        self.newline = Newline( parser, newline )

        # The node handles the raw text dumping a little different, because of
        # the support added for multiline listitem
        self.dumptext = rowmarkup + rowitem.dump() + self.newline.dump()

    def contlist( self, parser, textcontents, newline ) :
        self.dumptext += textcontents.dump() + newline
        if self.textcontents :
            self.textcontents.extendtextcontents( textcontents )
        else :
            self.textcontents = textcontents

    def children( self ) :
        return ( self.rowmarkup, self.textcontents, self.newline )

    def tohtml( self ) :
        html = ''
        mrkup = self.rowmarkup.lstrip( ' \t' )[:3]
        if mrkup in [ '|| ', '||=' ] and self.textcontents:
            contents = []
            [ contents.extend( item.contents )
              for item in self.textcontents.textcontents ]
            process_textcontent( contents )
            html += self.textcontents.tohtml()
        return html

    def style( self ) :
        if self.rowtype == FORMAT_BTABLESTYLE :
            style = self.rowmarkup.lstrip( ' \t' )[3:].lstrip( ' \t' )
            style = styleparser( style.rstrip( '| \t' ) )
        else :
            style = ''
        return style

    def dump( self ) :
        if self.textcontents or self.empty :
            text = self.dumptext
        else :
            raise ZWASTError( "dump() : No item available for BtableRow() node" )
        return text

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'btablerow : `%s`' % self.rowmarkup )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write( '\n' )
        if self.textcontents :
            self.textcontents.show()
        elif self.empty :
            self.empty.show()
        else :
            raise ZWASTError( "show() : No bqitem available for BtableRow() node" )


class TableRows( Node ) :
    """class to handle `table_rows` grammar."""

    def __init__( self, parser, row, pipe=None, newline=None  ) :
        """`row` is table_cells"""
        self.parser = parser
        self.rows   = [ (row, pipe, Newline( parser, newline )) ]

    def appendrow( self, row, pipe=None, newline=None ) :
        self.rows.append( (row, pipe, Newline( self.parser, newline )) )

    def tohtml( self ) :
        style   = 'border-top : 1px solid gray; border-left : 1px solid gray; '
        html    = '<table style="%s" cellspacing="0" cellpadding="5px" >' % \
                  style
        for row, pipe, newline in self.rows :
            html += '<tr>' + row.tohtml() + \
                    ( ( newline and newline.tohtml() ) or '' ) + \
                    '</tr>'
        html   += '</table>'
        return html

    def children( self ) :
        return self.rows

    def dump( self ) :
        return ''.join(
            [ row.dump() + (pipe or '') + (nl and nl.dump()) or ''
              for row, pipe, nl in self.rows ]
        )

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'table_rows: ' )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        rowcount = 1
        for row, pipe, nl in self.rows :
            buf.write( lead + '(row %s)\n' % rowcount )
            rowcount += 1
            row.show( buf, offset + 2, attrnames, showcoord )
            nl and nl.show( buf, offset + 2, attrnames, showcoord )


class TableCells( Node ) :
    """class to handle `table_cells` grammar."""

    def __init__( self, parser, markup, cell  ) :
        """`cell` can be `Empty` object or `TextContents` object"""
        self.parser = parser
        # `markup` captures the cell markup - pipe+style
        self.cells  = [ [markup, cell, 1] ]

    def appendcell( self, markup, cell ) :
        # `markup` captures the cell markup - pipe+style
        strippedmarkup  = markup.strip()
        colspan         = len(strippedmarkup) - len(strippedmarkup.lstrip( M_PIPE ))
        if colspan == 1 :
            self.cells.append([ markup, cell, 1 ])
        elif colspan > 1 :
            # If no content for this cell, then merge the cell with the
            # previous cell
            self.cells[-1][2] += colspan - 1 # By incrementing the colspan
            self.cells.append([ markup, cell, 1 ])

    def children( self ) :
        return ( self.cells, )

    def totalcells( self ) :
        return sum(
                [ 1
                  for markup, cell, colspan in self.cells 
                  if isinstance( cell, TextContents )
                ])

    def tohtml( self ) :
        # Process the text contents and convert them into html
        style     = 'padding : 5px; border-right : 1px solid gray; ' + \
                    'border-bottom : 1px solid gray;'
        htmlcells = []

        for markup, cell, colspan in self.cells :
            markup   = markup.strip()
            contents = []
            if isinstance( cell, TextContents ) :
                [ contents.extend( item.contents ) for item in cell.textcontents ]
                # Detect text alignment for the cell
                chtml = contents[-1].html
                if chtml and chtml[-1] == '$' :
                    style +=  ' ;text-align : right; '
                    contents[-1].html = chtml[-1][:-1]
            process_textcontent( contents )
            
            if markup[:2] == M_PIPEHEAD :
                begintag = '<th colspan="%s" style="%s">' % \
                            ( colspan, style + styleparser( markup[2:] ) )
                endtag   = '</th>'
            else :
                begintag = '<td colspan="%s" style="%s">' % \
                            ( colspan, style + styleparser( markup[1:] ) )
                endtag   = '</td>'

            cellcontnet = cell.tohtml()
            colspan     = cellcontnet and True or False
            htmlcells.append( begintag + cell.tohtml() + endtag )
        return ''.join( htmlcells )

    def dump( self ) :
        return ''.join(
            [ markup + cell.dump() for markup, cell, colspan in self.cells ]
        )

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'table_cells: ' )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        cellcount = 1
        for markup, cell, colspan in self.cells :
            buf.write( lead + '(cell %s)\n' % cellcount )
            cellcount += 1
            cell.show( buf, offset + 2, attrnames, showcoord )


class Lists( Node ) :
    """class to handle `orderedlists` and `unorderedlists` grammar."""

    def __init__( self, parser, l ) :
        self.parser = parser
        self.listitems = [ l ]

    def appendlist( self, l ) :
        self.listitems.append( l )

    def children( self ) :
        return self.listitems

    def tohtml( self ) :
        html         = ''
        closemarkups = []   # Stack to manage nested list.
        markups      = { '#' : ('<ol>', '</ol>'),
                         '*' : ('<ul>', '</ul>') }
        pm   = ''
        cm   = ''
        for l in self.listitems :
            patt     = re.compile( r'[\*\#]{1,5}$', re.MULTILINE | re.UNICODE )
            cm       = re.search( patt, l.listmarkup ).group()
            cmpmark  = cmp( len(pm), len(cm) )  # -1 or 0 or 1
            diffmark = abs( len(cm) - len(pm))  # 0 to 4
            if cmpmark > 0 :
                # previous list markup (pm) is one level deeper, so end the list
                html += ''.join([ closemarkups.pop() for i in range(diffmark) ])
            elif cmpmark < 0 :
                # current list markup (cm) is one level deeper, open a new list
                for i in range(diffmark) :
                    html += markups[cm[0]][0]
                    closemarkups.append( markups[cm[0]][1] )
            html += l.tohtml()
            pm = cm
        html += ''.join([ closemarkups.pop() for i in range(len(closemarkups)) ])
        return html

    def dump( self ) :
        return ''.join([ c.dump() for c in self.listitems ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        if showcoord :
            buf.write( ' (at %s)' % self.coord )

        for c in self.listitems :
            c.show( buf, offset + 2, attrnames, showcoord )


class List( Node ) :
    """class to handle `orderedlist` and `unorderedlist` grammar."""

    def __init__( self, parser, listtype, listmarkup, listitem, newline ) :
        self.parser = parser
        self.listtype     = listtype
        self.listmarkup   = listmarkup
        if isinstance( listitem, Empty ) :
            self.empty        = listitem
            self.textcontents = None
        elif isinstance( listitem, TextContents ) :
            self.empty        = None
            self.textcontents = listitem
        else :
            raise ZWASTError( "Unknown `listitem` for List() node" )
        self.newline  = Newline( parser, newline )

        # The node handles the raw text dumping a little different, because of
        # the support added for multiline listitem
        self.dumptext = listmarkup + listitem.dump() + self.newline.dump()

    def contlist( self, parser, textcontents, newline ) :
        self.dumptext += textcontents.dump() + newline
        if self.textcontents :
            self.textcontents.extendtextcontents( textcontents )
        else :
            self.textcontents = textcontents

    def children( self ) :
        return ( self.listtype, self.listmarkup, self.textcontents,
                 self.newline )

    def style( self ) :
        markup = self.listmarkup.strip( ' \t' )
        off    = markup.find('{')
        style  = off > 0 and styleparser( markup[off:] ) or ''
        return style

    def tohtml( self ) :
        # Process the text contents and convert them into html
        if self.textcontents :
            contents = []
            [ contents.extend( item.contents )
              for item in self.textcontents.textcontents ]
            process_textcontent( contents )
            html = '<li style="%s">%s</li>' % \
                        ( self.style(), self.textcontents.tohtml() )
        elif self.empty :
            html = '<li style="%s">%s</li>' % \
                        ( self.style(), self.empty.tohtml() )
        else :
            raise ZWASTError( "tohtml() : No listitem available for List() node" )
        return html

    def dump( self ) :
        if self.textcontents or self.empty :
            text = self.dumptext
        else :
            raise ZWASTError( "dump() : No listitem available for List() node" )
        return text

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        if self.listtype == 'ordered' :
            buf.write( lead + 'orderedlist: `%s` ' % self.listmarkup )
        if self.listtype == 'unordered' :
            buf.write( lead + 'unorderedlist: `%s` ' % self.listmarkup )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        if self.textcontents :
            self.textcontents.show()
        elif self.empty :
            self.empty.show()
        else :
            raise ZWASTError( "show() : No listitem available for List() node" )


class Definitions( Node ) :
    """class to handle `definitionlists` grammar."""

    def __init__( self, parser, definition ) :
        self.parser = parser
        self.listitems = [ definition ]

    def appendlist( self, definition ) :
        self.listitems.append( definition )

    def children( self ) :
        return self.listitems

    def tohtml( self ) :
        html         = '<dl>' + \
                       ''.join([ c.tohtml() for c in self.listitems ]) + \
                       '</dl>'
        return html

    def dump( self ) :
        return ''.join([ c.dump() for c in self.listitems ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        if showcoord :
            buf.write( ' (at %s)' % self.coord )

        for c in self.listitems :
            c.show( buf, offset + 2, attrnames, showcoord )

class Definition( Node ) :
    """class to handle `definitionlist` grammar."""

    def __init__( self, parser, defnmarkup, defnitem, newline ) :
        self.parser     = parser
        self.defnmarkup = defnmarkup
        defnmarkup      = defnmarkup.strip( ' \t' )
        self.dt         = defnmarkup[1:-2]
        if isinstance( defnitem, Empty ) :
            self.empty        = defnitem
            self.textcontents = None
        elif isinstance( defnitem, TextContents ) :
            self.empty        = None
            self.textcontents = defnitem
        else :
            raise ZWASTError( "Unknown `defnitem` for Definition() node" )
        self.newline      = Newline( parser, newline )

        # The node handles the raw text dumping a little different, because of
        # the support added for multiline listitem
        self.dumptext = defnmarkup + defnitem.dump() + self.newline.dump()

    def contlist( self, parser, textcontents, newline ) :
        self.dumptext += textcontents.dump() + newline
        if self.textcontents :
            self.textcontents.extendtextcontents( textcontents )
        else :
            self.textcontents = textcontents

    def children( self ) :
        return ( self.defnmarkup, self.textcontents, self.newline )

    def tohtml( self ) :
        # Process the text contents and convert them into html
        html = '<dt><b>' + self.dt + '</b></dt>'
        if self.textcontents :
            contents = []
            [ contents.extend( item.contents )
              for item in self.textcontents.textcontents ]
            process_textcontent( contents )
            dd = self.textcontents.tohtml()
        elif self.empty :
            dd = self.empty.tohtml()
        else :
            raise ZWASTError( 
                    "tohtml() : No defnitem available for Definition() node" )
        html += '<dd>' + dd + '</dd>'
        return html

    def dump( self ) :
        if self.textcontents or self.empty :
            text = self.dumptext
        else :
            raise ZWASTError(
                    "dump() : No defnitem available for Definition() node" )
        return text

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'definition: `%s` ' % self.defnmarkup )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        if self.textcontents :
            self.textcontents.show()
        elif self.empty :
            self.empty.show()
        else :
            raise ZWASTError(
                    "show() : No defnitem available for Definition() node" )


class BQuotes( Node ) :
    """class to handle `blockquotes` grammar."""

    def __init__( self, parser, bq ) :
        self.parser = parser
        self.listitems = [ bq ]

    def appendlist( self, bq ) :
        self.listitems.append( bq )

    def children( self ) :
        return self.listitems

    def _extendcontents( self, bq, contents ) :
        # Collect the contents that spans across muliple lines of same block
        # level. 'contents' is the accumulator
        if bq.textcontents :
            [ contents.extend( item.contents )
              for item in bq.textcontents.textcontents ]
        return

    def _processcontents( self, contents ) :
        # Process the accumulated contents
        process_textcontent( contents )
        html = ''.join([ cont.html for cont in contents ])
        return html

    def tohtml( self ) :
        html         = ''
        stylefirst   = 'border-left : 2px solid #d6d6d6; padding-left : 5px'
        stylerest    = 'margin-left : 0px; border-left : 2px solid #d6d6d6; padding-left : 5px'
        closemarkups = []   # Stack to manage nested list.
        contents = []
        pm   = ''
        cm   = ''
        for i in range(len(self.listitems)) :
            style    = (i == 0) and stylefirst or stylerest
            bq       = self.listitems[i]
            patt     = re.compile( r'[\>]{1,5}$', re.MULTILINE | re.UNICODE )
            cm       = re.search( patt, bq.bqmarkup ).group()
            cmpmark  = cmp( len(pm), len(cm) )  # -1 or 0 or 1
            diffmark = abs( len(cm) - len(pm))  # 0 or 1

            if cmpmark > 0 :
                # previous bq markup (pm) is one or more level deeper,
                # so end the blockquote(s)
                # And, process the accumulated content
                html     += self._processcontents( contents )
                contents = []

                html     += ''.join([ closemarkups.pop() for i in range(diffmark) ])

            elif cmpmark < 0 :
                # current bq markup (cm) is one or more level deeper, 
                # open new blockquote(s)
                # And, process the accumulated content
                html     += self._processcontents( contents )
                contents = []

                for j in range(diffmark-1) :
                    html += '<blockquote>'
                    closemarkups.append( '</blockquote>' )
                html += '<blockquote style="%s">' % style
                closemarkups.append( '</blockquote>' )

            self._extendcontents( bq, contents )
            contents.append( Content( self.parser, '\n', TEXT_NEWLINE, '<br></br>' ))
            # html += bq.tohtml()
            pm    = cm

        # Pop-out the last new-line (<br></br>)
        if contents[-1].html == '<br></br>' :
            contents.pop( -1 )

        html += self._processcontents( contents )
        html += ''.join([ closemarkups.pop() for i in range(len(closemarkups)) ])
        return html

    def dump( self ) :
        return ''.join([ c.dump() for c in self.listitems ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        if showcoord :
            buf.write( ' (at %s)' % self.coord )

        for c in self.listitems :
            c.show( buf, offset + 2, attrnames, showcoord )


class BQuote( Node ) :
    """class to handle `blockquote` grammar."""

    def __init__( self, parser, bqmarkup, bqitem, newline ) :
        self.parser   = parser
        self.bqmarkup = bqmarkup
        if isinstance( bqitem, Empty ) :
            self.empty        = bqitem
            self.textcontents = None
        elif isinstance( bqitem, TextContents ) :
            self.textcontents = bqitem
            self.empty        = None
        else :
            raise ZWASTError( "Unknown `bqitem` for BQuote() node" )
        self.newline      = Newline( parser, newline )

    def children( self ) :
        return ( self.bqmarkup, self.textcontents, self.newline )

    def tohtml( self ) :
        # This function is not used. The logic for html translation is with
        # BQuotes class

        # Process the text contents and convert them into html
        if self.textcontents :
            contents = []
            [ contents.extend( item.contents )
              for item in self.textcontents.textcontents ]
            process_textcontent( contents )
            html = self.textcontents.tohtml()
        elif self.empty :
            html = self.empty.tohtml()
        else :
            raise ZWASTError(
                    "tohtml() : No bqitem available for BQuote() node" )
        return html

    def dump( self ) :
        if self.textcontents :
            text = self.bqmarkup + self.textcontents.dump()  + \
                   self.newline.dump()
        elif self.empty :
            text = self.bqmarkup + self.empty.dump()  +\
                   self.newline.dump()
        else :
            raise ZWASTError(
                    "dump() : No bqitem available for BQuote() node" )
        return text

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'blockquote: `%s` ' % self.bqmarkup )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        if self.textcontents :
            self.textcontents.show()
        elif self.empty :
            self.empty.show()
        else :
            raise ZWASTError( "show() : No bqitem available for BQuote() node" )


class TextContents( Node ) :
    """class to handle `textcontents` grammar."""
    def __init__( self, parser, item  ) :  # item is Link or Macro or Html or BasicText
        self.parser = parser
        self.textcontents = [ item ]

    def appendcontent( self, item ) :      # item is Link or Macro or Html or BasicText
        self.textcontents.append( item )

    def extendtextcontents( self, textcontents ) : # item is Link or Macro or Html or BasicText
        if isinstance( textcontents, TextContents ) :
            self.textcontents.extend( textcontents.textcontents )

    def children( self ) :
        return self.textcontents

    def tohtml( self ) :
        return ''.join([ item.tohtml() for item in self.textcontents ])

    def dump( self ) :
        return ''.join([ item.dump() for item in self.textcontents ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'textcontent: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )

        for textcontent in self.textcontents :
            textcontent.show( buf, offset + 2, attrnames, showcoord )


class Link( Node ) :
    """class to handle `link` grammer.
    There are special links, 
        * - Open in new window,
        $ - Create an anchor
        + - Image"""

    def __init__( self, parser, link ) :
        self.parser = parser

        # parse the text
        tup  = link[2:-2].split( '|', 1 )
        href = tup and tup.pop(0).strip(' \t') or ''
        text = tup and escape_htmlchars(tup.pop(0)).strip(' \t') or ''

        # parse the href and for special notations
        html   =''
        prefix = href[:1]

        if prefix == '*' :              # Link - Open in new window
            html = '<a target="_blank" href="%s">%s</a>' % ( href[1:], text )

        elif prefix == '$' :            # Link - Anchor 
            html = '<a name="%s">%s</a>' % ( href[1:], text )

        elif prefix == '+' :            # Link - Image (actually no href)
            style = 'float: left;' if href[1:2] == '<' \
                                   else ( 'float: right;' if href[1:2] == '>' \
                                                          else '' )
            src   = href[1:].strip( '<>' )
            html  = '<img src="%s" alt="%s" style="%s"></img>' % ( 
                     src, text, style )

        elif parser.zwparser.app and \
             (parser.zwparser.app.name == 'zeta' and prefix == '@') :
                                        # Link - InterZeta or ZetaLinks
            import zwiki.zetawiki
            href, title, text, style = zwiki.zetawiki.parse_link(
                                                parser.zwparser, href, text
                                       )
            html = '<a href="%s" title="%s" style="%s">%s</a>' % ( 
                        href, title, style, text )

        elif href[:6] == "mailto" :
                                        # Link - E-mail
            if self.parser.zwparser.obfuscatemail :
                href = obfuscatemail(href)
                text = obfuscatemail(text) 

            html = '<a href="%s">%s</a>' % (href, text)

        else :
            html = '<a href="%s">%s</a>' % ( href, text )

        self.contents = [ Content( parser, link, TEXT_LINK, html ) ]

    def children( self ) :
        return self.contents

    def tohtml( self ) :
        return ''.join([ c.html for c in self.contents ])

    def dump( self ) :
        return ''.join([ c.text for c in self.contents ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'link: ' )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')


class Macro( Node ) :
    """class to handle `macro` grammer."""

    def __init__( self, parser, macro  ) :
        self.parser      = parser
        self.text        = macro
        self.macroobject = build_macro( self, macro )
        # Translate the macro object right here itself.
        html = self.macroobject.tohtml()
        html = html or ' '  # Dont leave html empty !!
        self.contents    = [ Content( parser, macro, TEXT_MACRO, html or ' ' ) ]

    def children( self ) :
        return self.contents

    def tohtml( self ) :
        return ''.join([ c.html for c in self.contents ])

    def dump( self ) :
        return ''.join([ c.text for c in self.contents ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'macro: `%s`' % self.macro )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')


class Html( Node ) :
    """class to handle `html` grammer."""

    def __init__( self, parser, html_text ) :
        self.parser = parser
        self.text   = html_text
        self.html   = html_text[2:-2]

        self.html   = tt.parsetag( self.html )

        self.contents = [ Content( parser, self.text, TEXT_HTML, self.html ) ]

    def children( self ) :
        return self.contents

    def tohtml( self ) :
        return ''.join([ c.html for c in self.contents ])

    def dump( self ) :
        return ''.join([ c.text for c in self.contents ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'html: `%s`' % self.html )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')


class BasicText( Node ) :
    """class to handle `basictext` grammar."""

    def __init__( self, parser, type, text  ) :
        self.parser = parser
        # self.contents as list of Content object

        if type == TEXT_SPECIALCHAR :
            self.contents = []
            virtuallines  = text.split( '\\\\' )
            self.contents.append(
                    Content( parser, virtuallines[0], TEXT_SPECIALCHAR,
                             escape_htmlchars( virtuallines[0] ))
            )
            for line in virtuallines[1:] :
                self.contents.append(
                    Content( parser, '\\\\', TEXT_SPECIALCHAR_LB, '<br></br>' )
                )
                self.contents.append( Content( parser, line, TEXT_SPECIALCHAR,
                                               escape_htmlchars(line) ))

        elif type == TEXT_HTTPURI :
            self.contents = [ Content( parser, 
                                       text, type,
                                       '<a href="'+text+ '">' + text + '</a>'
                              )
                            ]

        elif type == TEXT_WWWURI :
            self.contents = [ Content( parser,
                                       text, type,
                                       '<a href="http://%s">%s</a>' % (text,text)
                              )
                            ]
        
        elif type[:2] == 'm_' :
            self.contents = [ Content( parser, text, type ) ]

        else : # TEXT_ZWCHARPIPE, TEXT_ALPHANUM, TEXT_ESCAPED
            self.contents = [ Content( parser, text, type, text ) ]

    def children( self ) :
        return self.contents

    def tohtml( self ):
        return ''.join([ c.html for c in self.contents ])

    def dump( self ) :
        text = ''
        for c in self.contents :
            text += [ c.text, '~' + c.text ][ c.type == TEXT_ESCAPED ]
        return text

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write(lead + 'basictext :' )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')


class ParagraphSeparator( Node ) :
    """class to handle `paragraph_separator` grammar."""

    def __init__( self, parser, *args ) :
        self.parser  = parser
        self.newline = None
        self.empty   = None
        self.paragraph_separator = None
        if len(args) == 1 :
            if args[0] == '\n' or args[0] == '\r\n' :
                self.newline = Newline( parser, args[0] )
            elif isinstance( args[0], Empty ) :
                self.empty   = args[0]
        elif len(args) == 2 :
            self.paragraph_separator = args[0]
            self.newline             = Newline( parser, args[1] )

    def children( self ) :
        childnames = [ 'newline', 'empty', 'paragraph_separator' ]
        nodes      = filter(
                        None,
                        [ getattr( self, attr, None ) for attr in childnames ]
                     )
        return tuple(nodes)

    def tohtml( self ) :
        return ''.join([ c.tohtml() for c in self.children() ])

    def dump( self ) :
        return ''.join([ c.dump() for c in self.children() ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write(lead + 'paragraph_separator: ')

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        for c in self.children() :
            c.show( buf, offset + 2, attrnames, showcoord )


class Empty( Node ) :
    """class to handle `empty` grammar"""

    def __init__( self, parser ) :
        self.parser = parser

    def children( self ) :
        return ()

    def tohtml( self ):
        return ''

    def dump( self ) :
        return ''

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write(lead + 'empty: ')
        buf.write('\n')


class Newline( Node ) :
    """class to handle `newline` grammer"""

    def __init__( self, parser, newline ) :
        self.parser = parser
        self.newline = newline

    def children( self ) :
        return ( self.newline, )

    def tohtml( self ):
        return self.newline

    def dump( self ) :
        return self.newline

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write(lead + 'newline: ')
        buf.write('\n')
