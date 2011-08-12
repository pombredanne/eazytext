
from   StringIO             import StringIO



def body( *args, **kwargs ) :  
  _m.pushbuf()
  _m.extend( ['<html><body>', '<article>', '<style type="text/css"> .etpage {\n  white-space : normal\n}\n.etblk {\n}\n\n/* Text styling */\nspan.etmark {\n}\nstrong.etmark {\n}\nem.etmark {\n}\nu.etmark {\n}\nsup.etmark {\n}\nsub.etmark {\n}\nstrong.etmark > em.etmark {\n}\nstrong.etmark > u.etmark {\n}\nem.etmark > u.etmark {\n}\nstrong.etmark > em.etmark > u.etmark {\n}\np.ettext {\n}\n\n/* Sections */\nh1.etsec {\n}\nh2.etsec {\n}\nh3.etsec {\n}\nh4.etsec {\n}\nh5.etsec {\n}\nh1 a.etseclink, h2 a.etseclink, h3 a.etseclink, h4 a.etseclink, h5 a.etseclink {\n  color: #CCCCCC;\n  font-size: medium;\n  text-decoration: none\n}\n\n/* Small table */\ntable.ettbl {\n  border-collapse: collapse;\n}\ntr.ettbl {\n}\nth.ettbl {\n  padding : 5px; border: 1px solid gray;\n}\ntd.ettbl {\n  padding : 5px; border: 1px solid gray;\n}\n\n/* Big table */\ntable.etbtbl {\n  border-collapse: collapse;\n}\ntr.etbtbl {\n}\nth.etbtbl {\n  padding : 5px; border : 1px solid gray;\n}\ntd.etbtbl {\n  padding : 5px; border : 1px solid gray;\n}\n\n/* Horizontal rule */\nhr.ethorz {\n}\n\n/* List */\nul.et {\n}\nol.et {\n}\nli.et {\n}\n\n/* Definitions */\ndl.et {\n}\ndt.et {\n}\ndd.et {\n}\n\n/* Blockquote */\nblockquote.et.firstlevel {\n  border-left : 2px solid #d6d6d6;\n  padding-left : 5px\n}\nblockquote.et.innerlevel {\n  margin-left : 0px;\n  border-left : 2px solid #d6d6d6;\n  padding-left : 5px;\n}\n\n/* Links */\nimg.et {\n}\na.etlink {\n}\na.etlink.anchor {\n}\na.ethttpuri {\n}\na.etwwwuri {\n}\n\n/* macro-anchor */\na.etm-anchor {\n}\n\n/* macro-clear */\ndiv.etm-clear {\n  clear : both;\n}\n\n/* macro-image */\ndiv.etm-image {\n  margin    : 0px;\n  padding   : 0px;\n  border    : 0px;\n}\n\n/* macro-images */\ntable.etm-images {\n  margin    : 10px;\n  padding   : 0px;\n  border    : 0px;\n}\ntable.etm-images tr {\n}\ntable.etm-images td {\n}\ntable.etm-images img {\n}\n\n/* macro-span */\nspan.etm-span {\n  color   : gray;\n  padding : 2px;\n}\n\n/* macro-toc */\ndetails.etm-toc {\n  background    : #f8f7bc;\n  position      : relative;\n  float         : left;\n  margin        : 10px;\n  padding       : 3px;\n  width         : 20em;\n  border-right  : 1px solid gray;\n  border-bottom : 1px solid gray;\n}\ndetails.etm-toc summary {\n  font-weight : bold;\n  color : blue;\n  cursor : pointer;\n  font-size : small;\n  position: relative;\n  float: right;\n}\ndetails.etm-toc ul {\n  list-style : none;\n}\ndetails.etm-toc a {\n}\ndetails.etm-toc a.level-1 {\n  margin-left : 0em;\n}\ndetails.etm-toc a.level-2 {\n  margin-left : 0.7em;\n}\ndetails.etm-toc a.level-3 {\n  margin-left : 1.4em;\n}\ndetails.etm-toc a.level-4 {\n  margin-left : 2.1em;\n}\ndetails.etm-toc a.level-5 {\n  margin-left : 2.8em;\n}\ndetails.etm-toc a.level-6 {\n  margin-left : 3.5em;\n}\n\n/* extension-box */\ndiv.etext-box .box {\n  color         : gray;\n  border-top    : thin solid gray;\n  border-right  : thin solid gray;\n  border-bottom : thin solid gray;\n  border-left   : thin solid gray;\n}\ndiv.etext-box .boxtitle = {\n  color          : black;\n  background     : #EEEEEE;\n  font-weight    : bold;\n  padding-top    : 3px;\n  padding-right  : 3px;\n  padding-bottom : 3px;\n  padding-left   : 3px;\n}\ndiv.etext-box .boxcont = {\n  padding-top    : 3px;\n  padding-right  : 3px;\n  padding-bottom : 3px;\n  padding-left   : 3px;\n}\ndiv.etext-box span.boxhide {\n  display: none;\n  float: right;\n  font-size : xx-small;\n  color: blue;\n  cursor: pointer;\n}\ndiv.etext-box span.boxshow {\n  display: none;\n  float: right;\n  font-size : xx-small;\n  color: blue;\n  cursor: pointer;\n}\n\n\n/* extension-code */\ndiv.etext-code {\n  margin-left  : 5%;\n  margin-right : 5%;\n}\ndiv.etext-code .highlighttable td.linenos {\n  padding : 3px;\n  color : brown;\n  background-color : activeborder;\n}\ndiv.etext-code .highlighttable td.code {\n  padding : 3px\n}\ndiv.etext-code .highlight {\n  background-color : #FAFAFA;\n}\ndiv.etext-code .codecont {\n  background : #FAFAFA;\n  border : 1px dashed gray;\n}\n\n/* extension-footnote */\ndiv.etext-footnote .footnote {\n}\ndiv.etext-footnote table {\n  margin-left: 5px;\n}\ndiv.etext-footnote td.anchor {\n  padding: 5px;\n  color: blue;\n  vertical-align: top;\n}\ndiv.etext-footnote td.notes {\n  padding: 5px;\n  text-align: left;\n}\n\n/* extension-html */\ndiv.etext-html .html {\n}\n\n/* extension-nested */\ndiv.etext-nested .nested {\n}\n\n/* Templated tags */\nspan.etttag.pre {\n  white-space : pre;\n  font-family : monospace;\n}\nabbr.etttag {\n}\nspan.etttag.fixme {\n  border : 1px solid cadetBlue;\n  color : red;\n  padding: 1px;\n  font-family : monospace;\n}\ndiv.etttag.qbq {\n  font-style : italic;\n  margin : 5px 0px 5px 0px;\n  padding : 15px 0px 10px 40px;\n  width: 70%;\n  white-space: pre;\n}\nspan.etttag.smile {\n  font-size: x-large;\n  color: darkOrchid;\n  padding: 1px;\n  font-family : monospace;\n}\nspan.etttag.sad {\n  font-size: x-large;\n  color: orangeRed;\n  padding: 1px;\n  font-family : monospace;\n}\naddress.etttag {\n}\nspan.etttag.fnt {\n}\nsup.etttag.footnote {\n}\nsup.etttag.footnote a {\n  text-decoration: none;\n}\n </style>', '<p class="ettext">\n', u'This', u' ', u'file', u' ', u'contains', u' ', u'an', u' ', u'unclosed', u' ', u'no', u'-', u'wiki', u' ', u'block', u' ', u"{{{ Box\n\n\n= Top-level heading \n    This sample markup is taken from creole and modified to eazytext markup.\n\n    Goto [[ #Subsub | other heading markups ]] for more ...     Goto [[ #anchor in list | anchor created using anchor macro ]]\n\n== Some text markup\nYou can make things ''bold'' or //italic// or '/both'/ but /'not this one'/.\nMore formatting, __ underline __\nsuperscripting, x^^2^^\nsubscripting, log,,2,,7\n'/_ bold italic underline '/_\nAlso possible to, have '_ underlined bold '_ and /_italic underline/_\nthis is still bold''.\nsingle-quotes.\nNot bold. Character formatting does not cross paragraph boundaries.\nThis line is single line \\ but uses line break markup to split the line.\n\nEmpty markups are '''' //// are ignored.\n\nAnd, complex markups like '' hello // world // \\ is treated like this ''\n\nAn example for indentation, {{ Span( 'Second level', style={ 'margin-left' : '4em'} ) }}", u' ', u'\n', '</p>\n', '<h3 class="etsec" style="">', u' ', u'Text', u' ', u'with', u' ', u'html', u' ', u'special', u' ', u'chars', u'<a id=" Text with html special chars"></a>', u'<a class="etseclink" href="# Text with html special chars" title="Link to this section">&#9875;</a>', u'\n', '</h3>\n', u'\n', '<blockquote class="et firstlevel">\n', '<blockquote class="et innerlevel">\n', '<blockquote class="et innerlevel">\n', u' ', u'it', u' ', u'=', u' ', u'[', u' ', u'1', u',', u' ', u'2', u',', u' ', u'3', u',', u' ', u']', u' ', u' ', u' ', u'&gt;', u'&gt;', u'&gt;', u' ', u'print', u' ', u'type(it)', u' ', u' ', u' ', u' ', u' ', u' ', u' ', u' ', u' ', u' ', u'&lt;', u' ', u'List', u' ', u' ', u'type', u' ', u'...', u' ', u'&gt;', u'\n', '</blockquote>\n', '</blockquote>\n', '</blockquote>\n', u'\n', '<h2 class="etsec" style="">', u' ', u'Links', u'<a id=" Links"></a>', u'<a class="etseclink" href="# Links" title="Link to this section">&#9875;</a>', u'\n', '</h2>\n', u'\n', '<p class="ettext">\n', u'You', u' ', u'can', u' ', u'use', u' ', u'<a class="etlink" target="" href="internal links">internal links</a>', u' ', u'or', u' ', u'<a class="etlink" target="" href="http://www.wikicreole.org">external links</a>', u',', u'\n', u'Here', u"'", u's', u' ', u'another', u' ', u'sentence', u':', u' ', u'This', u' ', u'wisdom', u' ', u'is', u' ', u'taken', u' ', u'from', u' ', u'<a class="etlink" target="" href="Ward Cunningham\'s">Ward Cunningham\'s</a>', u'\n', u'<a class="etlink" target="" href="http://www.c2.com/doc/wikisym/WikiSym2006.pdf">Presentation at the Wikisym 06</a>', u'.', u'\n', '</p>\n', u'\n', '<p class="ettext">\n', u'Here', u"'", u's', u' ', u'a', u' ', u'external', u' ', u'link', u' ', u'without', u' ', u'a', u' ', u'description', u':', u' ', u'<a class="etlink" target="" href="http://www.wikicreole.org">http://www.wikicreole.org</a>', u'\n', '</p>\n', u'\n', '<p class="ettext">\n', u'Be', u' ', u'careful', u' ', u'that', u' ', u'italic', u' ', u'links', u' ', u'are', u' ', u'rendered', u' ', u'properly', u':', u' ', u' ', '<em class="etmark" style="">', u'<a class="etlink" target="" href="http://my.book.example/">My Book Title</a>', '</em>', u' ', u'\n', '</p>\n', u'\n', '<p class="ettext">\n', u'Free', u' ', u'links', u' ', u'without', u' ', u'braces', u' ', u'should', u' ', u'be', u' ', u'rendered', u' ', u'as', u' ', u'well', u',', u' ', u'like', u' ', u'<a class="ethttpuri" href="http://www.wikicreole.org/">http://www.wikicreole.org/</a>', u' ', u'and', u' ', u'<a class="ethttpuri" href="http://www.wikicreole.org/users/">http://www.wikicreole.org/users/</a>', u'~example.', u' ', u'\n', '</p>\n', u'\n', '<p class="ettext">\n', u'Creole1.0', u' ', u'specifies', u' ', u'that', u' ', u'<a class="ethttpuri" href="http://bar">http://bar</a>', u' ', u'and', u' ', u'ftp', u':', '<em class="etmark" style="">', u'bar', u' ', u'should', u' ', u'not', u' ', u'render', u' ', u'italic', u',', u'\n', u'something', u' ', u'like', u' ', u'foo', u':', '</em>', u'bar', u'//', u' ', u'should', u' ', u'render', u' ', u'as', u' ', u'italic.', u'\n', u'You', u' ', u'can', u' ', u'use', u' ', u'this', u' ', u'to', u' ', u'draw', u' ', u'a', u' ', u'line', u' ', u'to', u' ', u'separate', u' ', u'the', u' ', u'page', u':', u'\n', '</p>\n', '<hr class="ethorz"/>\n', u'\n', u'\n', u'\n', '<h2 class="etsec" style="">', u' ', u'wiki', u' ', u'extension', u' ', u'=', u'=', u'<a id=" wiki extension =="></a>', u'<a class="etseclink" href="# wiki extension ==" title="Link to this section">&#9875;</a>', u'\n', '</h2>\n', u'\n', '<p class="ettext">\n', u'You', u' ', u'can', u' ', u'use', u' ', u'nowiki', u' ', u'syntax', u' ', u'if', u' ', u'you', u' ', u'would', u' ', u'like', u' ', u'do', u' ', u'stuff', u' ', u'like', u' ', u'this', u':', u'\n', '</p>\n', u"# 'border-bottom' : 'thin solid green', 'background' : 'Aquamarine', }\nThis is a sample box written using wiki extensions. Note that the width is\nadjustable and you can even position it.\n\n== list\nYou can use lists, start it at the first column for now, please...\n\nunnumbered lists are like\n* item a\n* item b\n* ''bold item c''\n\nblank space is also permitted before lists like:\n  *   item a\n * item b\n ** item c.a\n\nor you can number them\n# [[item 1]]\n# item 2\n# // italic item 3 //\n    ## item 3.1\n  ## item 3.2\n\nup to five levels\n* level 1\n** level 2\n*** level 3\n**** level 4\n***** level 5\n=== All possible list combination\n\n* level 1 item 1 unordered\n* level 1 item 2 unordered\n** level 2 item 1 unordered {{ Anchor( 'anchor in list', 'Anchored here', style={ 'font-weight' : 'bold' } ) }}\n** level 2 item 2 unordered\n* level 1 item 1 unordered\n* level 1 item 2 unordered\n## level 2 item 1 ordered\n## level 2 item 2 ordered\n*** level 3 item 1 unordered\n*** level 3 item 2 unordered\n## level 2 item 1 ordered\n## level 2 item 2 ordered\n# level 1 item 1 ordered\n## level 2 item 1 ordered\n* level 1 item 1 unordered\n* level 1 item 2 unordered\n\n=== All possible list combinations in a table\n\n{{ Html( '&lt;table border=&quot;1&quot; &gt;' ) }}\n{{ Html( '&lt;tr&gt;' ) }}\n{{ Html( '&lt;td&gt;' ) }}\n** level 2 item 1 unordered {{ Anchor( 'anchor in list', 'Anchored here', style={ 'font-weight' : 'bold' } ) }}\n** level 2 item 2 unordered\n* level 1 item 1 unordered\n{{ Html( '&lt;/td&gt;' ) }}\n{{ Html( '&lt;td&gt;' ) }}\n## level 2 item 1 ordered\n## level 2 item 2 ordered\n{{ Html( '&lt;/td&gt;' ) }}\n{{ Html( '&lt;/tr&gt;' ) }}\n{{ Html( '&lt;tr&gt;' ) }}\n{{ Html( '&lt;td&gt;' ) }}\n*** level 3 item 1 unordered\n{{ Html( '&lt;/td&gt;' ) }}\n{{ Html( '&lt;td&gt;' ) }}\n*** level 3 item 2 unordered\n{{ Html( '&lt;/td&gt;' ) }}\n{{ Html( '&lt;/tr&gt;' ) }}\n{{ Html( '&lt;tr&gt;' ) }}\n{{ Html( '&lt;td&gt;' ) }}\n## level 2 item 1 ordered\n## level 2 item 2 ordered\n# level 1 item 1 ordered\n## level 2 item 1 ordered\n## level 2 item 2 ordered\n{{ Html( '&lt;/td&gt;' ) }}\n* level 1 item 2 unordered\n{{ Html( '&lt;/tr&gt;' ) }}\n{{ Html( '&lt;/table&gt;' ) }}\n\nYou cannot have\n\n== Macros ==\n\nThis line demonstrates the {{Span( 'Span Macro', color='green', border='thin solid red' )}}\n\n== Box Wiki extensions ===\n{{{ Box\n#   'margin' : '10px 2px 10px 5px;',\n#   'title'  : 'Priestley Avenue side of the Joseph Priestley House in 2007',\n# }\n\nThe Joseph Priestley House was the American home of 18th-century British\ntheologian, dissenting clergyman, natural philosopher, educator, and\npolitical theorist Joseph Priestley from 1798 until his death in 1804.\nLocated in Northumberland, Pennsylvania, the house, which was designed by\nPriestley's wife Mary, is Georgian with Federalist accents. The\n''Pennsylvania Historical'' and ''Museum Commission'' has operated it as a museum\ndedicated to Joseph Priestley since 1970, but may close it by July 2009\ndue to low visitation and budget cuts. \n* Fleeing religious persecution and political turmoil in Britain, the Priestleys emigrated to the United States in 1794 seeking a peaceful life.\n* Hoping to avoid the political troubles that had plagued them in Britain and the problems of urban life they saw in the United States, the Priestleys built a house in rural Pennsylvania; nevertheless, political disputes and family troubles dogged Priestley during the last ten years of his life.\n*In the 1960s, the house was carefully restored by the Pennsylvania Historical and Museum Commission and designated a National Historic Landmark.\n* A second renovation was undertaken in the 1990s to return the home to the way it looked during Priestley's time.\n(more...)\n\nRecently featured: Retiarius - Niobium - Emma Watson\n", u'\n', '<ol class="et">', '<li class="et" style="">', u' ', u'{', u' ', u"'", u'width', u"'", u' ', u' ', u':', u' ', u"'", u'48%', u"'", u',', u'\n', '</li>', '<li class="et" style="">', u' ', u' ', u' ', u"'", u'margin', u"'", u' ', u':', u' ', u"'", u'10px', u' ', u'5px', u' ', u'10px', u' ', u'2px;', u"'", u',', u'\n', '</li>', '<li class="et" style="">', u' ', u' ', u' ', u"'", u'title', u"'", u' ', u' ', u':', u' ', u"'", u'In', u' ', u'the', u' ', u'News', u"'", u',', u'\n', '</li>', '<li class="et" style="">', u' ', u'}', u'\n', u'Four', u' ', u'people', u' ', u'associated', u' ', u'with', u' ', u'the', u' ', u'torrent', u' ', u'tracking', u' ', u'website', u' ', u'The', u' ', u'Pirate', u' ', u'Bay', u',', u'\n', u'including', u' ', u'co', u'-', u'founder', u' ', u'Peter', u' ', u'Sunde', u' ', u'(pictured)', u',', u' ', u'are', u' ', u'found', u' ', u'guilty', u' ', u'of', u' ', u'promoting', u'\n', u'copyright', u' ', u'infringements.', u'\n', u'The', u' ', u'birth', u' ', u'of', u' ', u'Injaz', u',', u' ', u'the', u' ', u'world', u"'", u's', u' ', u'first', u' ', u'cloned', u' ', u'camel', u',', u' ', u'is', u' ', u'announced', u' ', u'in', u' ', u'Dubai', u',', u'\n', u'United', u' ', u'Arab', u' ', u'Emirates.', u'\n', u'A', u' ', u'fire', u' ', u'at', u' ', u'a', u' ', u'homeless', u' ', u'hostel', u' ', u'in', u' ', u'Kamien', u' ', u'Pomorski', u',', u' ', u'Poland', u',', u' ', u'kills', u' ', u'at', u' ', u'least', u' ', u'21', u'\n', u'people', u' ', u'and', u' ', u'injures', u' ', u'at', u' ', u'least', u' ', u'20', u' ', u'others', u' ', u'in', u' ', u'the', u' ', u'country', u"'", u's', u' ', u'deadliest', u' ', u'fire', u'\n', u'disaster', u' ', u'since', u' ', u'1980.', u'\n', u'In', u' ', u'golf', u',', u' ', u'Angel', u' ', u'Cabrera', u' ', u'of', u' ', u'Argentina', u' ', u'wins', u' ', u'the', u' ', u'2009', u' ', u'Masters', u' ', u'Tournament', u',', u' ', u'after', u'\n', u'a', u' ', u'sudden', u'-', u'death', u' ', u'playoff.', u'\n', u'cancellation', u' ', u'of', u' ', u'the', u' ', u'Fourth', u' ', u'East', u' ', u'Asia', u' ', u'Summit.', u'\n', u'}', u'}', u'}', u'\n', '</li>', '</ol>', u'\n', '<p class="ettext">\n', '<div class="etm-clear" style=""></div>', u'\n', '</p>\n', u'\n', '<p class="ettext">\n', u'eazytext', u' ', u'does', u' ', u'not', u' ', u'support', u' ', u'{{{ inline no-wiki }}', u'}', u' ', u'instead', u' ', u'use', u'\n', '</p>\n', u'\n', u'\n', u'&lt;div&gt; Hello world &lt;/div&gt;\n', u'\n', '<h1 class="etsec" style="">', u' ', u'Escapes', u' ', u'=', u'<a id=" Escapes ="></a>', u'<a class="etseclink" href="# Escapes =" title="Link to this section">&#9875;</a>', u'\n', '</h1>\n', '<p class="ettext">\n', u'Normal', u' ', u'Link', u':', u' ', u'<a class="ethttpuri" href="http://wikicreole.org/">http://wikicreole.org/</a>', u' ', u'-', u' ', u'now', u' ', u'same', u' ', u'link', u',', u' ', u'but', u' ', u'escaped', u':', u' ', u'~http', u':', u'//', u'wikicreole.org', u'/', u' ', u'\n', '</p>\n', u'\n', '<p class="ettext">\n', u'Normal', u' ', u'asterisks', u':', u' ', u'~', '<strong class="etmark" style="">', u'not', u' ', u'bold~', '</strong>', u'\n', '</p>\n', u'\n', '<p class="ettext">\n', u'a', u' ', u'tilde', u' ', u'alone', u':', u' ', u'~', u' ', u'\n', '</p>\n', u'\n', '<p class="ettext">\n', u'a', u' ', u'tilde', u' ', u'escapes', u' ', u'itself', u':', u' ', u'~~xxx', u'\n', '</p>\n', u'\n', '<p class="ettext">\n', u'Tables', u' ', u'are', u' ', u'done', u' ', u'like', u' ', u'this', u':', u'\n', '</p>\n', u'\n', '<table class="ettbl">\n', '<tr class="ettbl">\n', '<th class="ettbl" colspan="1" style="">', u'header', u' ', u'col1', '</th>\n', '<th class="ettbl" colspan="1" style="">', u'header', u' ', u'col2', '</th>\n', '<td class="ettbl" colspan="3" style="">', u' ', '</td>\n', u'\n', '</tr>\n', '<tr class="ettbl">\n', '<td class="ettbl" colspan="1" style="">', u'col1', '</td>\n', '<td class="ettbl" colspan="1" style="">', u'col2', '</td>\n', '<td class="ettbl" colspan="3" style="">', u' ', u'col3', '</td>\n', u'\n', '</tr>\n', '<tr class="ettbl">\n', '<td class="ettbl" colspan="1" style="">', u'you', '</td>\n', '<td class="ettbl" colspan="4" style="">', u'can', '</td>\n', u'\n', '</tr>\n', '<tr class="ettbl">\n', '<td class="ettbl" colspan="1" style="">', u'also', '</td>\n', '<td class="ettbl" colspan="2" style="">', u'align', u' ', u'it.', '</td>\n', '<td class="ettbl" colspan="2" style="">', u' ', u'col4', '</td>\n', u'\n', '</tr>\n', '</table>\n', u'\n', '<p class="ettext">\n', u'You', u' ', u'can', u' ', u'format', u' ', u'an', u' ', u'address', u' ', u'by', u' ', u'simply', u' ', u'forcing', u' ', u'linebreaks', u':', u'\n', u'My', u' ', u'contact', u' ', u'dates', u':', u'Pone', u':', u' ', u'xyzFax', u':', u' ', u'+45Mobile', u':', u' ', u'abc', u'\n', '</p>\n', u'\n', '<table class="ettbl">\n', '<tr class="ettbl">\n', '<th class="ettbl" colspan="1" style="">', u' ', u'Header', u' ', u'title', '</th>\n', '<th class="ettbl" colspan="2" style="">', u' ', u'Another', u' ', u'header', u' ', u'title', '</th>\n', u'\n', '</tr>\n', '<tr class="ettbl">\n', '<td class="ettbl" colspan="1" style="">', u' ', '<em class="etmark" style="">', u'italic', u' ', u'text', '</em>', '</td>\n', '<td class="ettbl" colspan="2" style="">', u' ', '<strong class="etmark" style="">', u' ', u' ', u'bold', u' ', u'text', u' ', '</strong>', '</td>\n', u'\n', '</tr>\n', '</table>\n', u'\n', '<p class="ettext">\n', u'If', u' ', u'interwiki', u' ', u'links', u' ', u'are', u' ', u'setup', u' ', u'in', u' ', u'your', u' ', u'wiki', u',', u' ', u'this', u' ', u'links', u' ', u'to', u' ', u'the', u' ', u'WikiCreole', u' ', u'page', u' ', u'about', u' ', u'Creole', u' ', u'1.0', u' ', u'test', u' ', u'cases', u':', u' ', u'<a class="etlink" target="" href="WikiCreole:Creole1.0TestCases">WikiCreole:Creole1.0TestCases</a>', u'.', u'\n', '</p>\n', u'\n', '<h4 class="etsec" style="">', u' ', u'Subsub', u'<a id=" Subsub"></a>', u'<a class="etseclink" href="# Subsub" title="Link to this section">&#9875;</a>', u'\n', '</h4>\n', '<h5 class="etsec" style="">', u' ', u'Subsubsub', u'<a id=" Subsubsub"></a>', u'<a class="etseclink" href="# Subsubsub" title="Link to this section">&#9875;</a>', u'\n', '</h5>\n', u'\n', '<h1 class="etsec" style="">', u' ', u'Top', u'-', u'level', u' ', u'heading', u' ', u'(1)', u' ', u'=', u'<a id=" Top-level heading (1) ="></a>', u'<a class="etseclink" href="# Top-level heading (1) =" title="Link to this section">&#9875;</a>', u'\n', '</h1>\n', '<h2 class="etsec" style="">', u' ', u'This', u' ', u'a', u' ', u'test', u' ', u'for', u' ', u'creole', u' ', u'0.1', u' ', u'(2)', u' ', u'=', u'=', u'<a id=" This a test for creole 0.1 (2) =="></a>', u'<a class="etseclink" href="# This a test for creole 0.1 (2) ==" title="Link to this section">&#9875;</a>', u'\n', '</h2>\n', '<h4 class="etsec" style="">', u' ', u'Subsub', u' ', u'(4)', u' ', u'=', u'=', u'=', u'=', u'<a id=" Subsub (4) ===="></a>', u'<a class="etseclink" href="# Subsub (4) ====" title="Link to this section">&#9875;</a>', u'\n', '</h4>\n', u'\n', '</article>', '</body></html>'] )
  return _m.popbuftext()

# ---- Footer

_etxhash = None
_etxfile = '/home/pratap/mybzr/pratap/dev/eazytext/eazytext/test/stdfiles/sample1.etx'