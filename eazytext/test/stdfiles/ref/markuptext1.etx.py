
from   StringIO             import StringIO



def body( *args, **kwargs ) :  
  _m.pushbuf()
  _m.extend( ['<html><body>', '<article>', '<style type="text/css"> .etpage {\n  white-space : normal\n}\n.etblk {\n}\n\n/* Text styling */\nspan.etmark {\n}\nstrong.etmark {\n}\nem.etmark {\n}\nu.etmark {\n}\nsup.etmark {\n}\nsub.etmark {\n}\nstrong.etmark > em.etmark {\n}\nstrong.etmark > u.etmark {\n}\nem.etmark > u.etmark {\n}\nstrong.etmark > em.etmark > u.etmark {\n}\np.ettext {\n}\n\n/* Sections */\nh1.etsec {\n}\nh2.etsec {\n}\nh3.etsec {\n}\nh4.etsec {\n}\nh5.etsec {\n}\nh1 a.etseclink, h2 a.etseclink, h3 a.etseclink, h4 a.etseclink, h5 a.etseclink {\n  color: #CCCCCC;\n  font-size: medium;\n  text-decoration: none\n}\n\n/* Small table */\ntable.ettbl {\n  border-collapse: collapse;\n}\ntr.ettbl {\n}\nth.ettbl {\n  padding : 5px; border: 1px solid gray;\n}\ntd.ettbl {\n  padding : 5px; border: 1px solid gray;\n}\n\n/* Big table */\ntable.etbtbl {\n  border-collapse: collapse;\n}\ntr.etbtbl {\n}\nth.etbtbl {\n  padding : 5px; border : 1px solid gray;\n}\ntd.etbtbl {\n  padding : 5px; border : 1px solid gray;\n}\n\n/* Horizontal rule */\nhr.ethorz {\n}\n\n/* List */\nul.et {\n}\nol.et {\n}\nli.et {\n}\n\n/* Definitions */\ndl.et {\n}\ndt.et {\n}\ndd.et {\n}\n\n/* Blockquote */\nblockquote.et.firstlevel {\n  border-left : 2px solid #d6d6d6;\n  padding-left : 5px\n}\nblockquote.et.innerlevel {\n  margin-left : 0px;\n  border-left : 2px solid #d6d6d6;\n  padding-left : 5px;\n}\n\n/* Links */\nimg.et {\n}\na.etlink {\n}\na.etlink.anchor {\n}\na.ethttpuri {\n}\na.etwwwuri {\n}\n\n/* macro-anchor */\na.etm-anchor {\n}\n\n/* macro-clear */\ndiv.etm-clear {\n  clear : both;\n}\n\n/* macro-image */\ndiv.etm-image {\n  margin    : 0px;\n  padding   : 0px;\n  border    : 0px;\n}\n\n/* macro-images */\ntable.etm-images {\n  margin    : 10px;\n  padding   : 0px;\n  border    : 0px;\n}\ntable.etm-images tr {\n}\ntable.etm-images td {\n}\ntable.etm-images img {\n}\n\n/* macro-span */\nspan.etm-span {\n  color   : gray;\n  padding : 2px;\n}\n\n/* macro-toc */\ndetails.etm-toc {\n  background    : #f8f7bc;\n  position      : relative;\n  float         : left;\n  margin        : 10px;\n  padding       : 3px;\n  width         : 20em;\n  border-right  : 1px solid gray;\n  border-bottom : 1px solid gray;\n}\ndetails.etm-toc summary {\n  font-weight : bold;\n  color : blue;\n  cursor : pointer;\n  font-size : small;\n  position: relative;\n  float: right;\n}\ndetails.etm-toc ul {\n  list-style : none;\n}\ndetails.etm-toc a {\n}\ndetails.etm-toc a.level-1 {\n  margin-left : 0em;\n}\ndetails.etm-toc a.level-2 {\n  margin-left : 0.7em;\n}\ndetails.etm-toc a.level-3 {\n  margin-left : 1.4em;\n}\ndetails.etm-toc a.level-4 {\n  margin-left : 2.1em;\n}\ndetails.etm-toc a.level-5 {\n  margin-left : 2.8em;\n}\ndetails.etm-toc a.level-6 {\n  margin-left : 3.5em;\n}\n\n/* extension-box */\ndiv.etext-box .box {\n  color         : gray;\n  border-top    : thin solid gray;\n  border-right  : thin solid gray;\n  border-bottom : thin solid gray;\n  border-left   : thin solid gray;\n}\ndiv.etext-box .boxtitle = {\n  color          : black;\n  background     : #EEEEEE;\n  font-weight    : bold;\n  padding-top    : 3px;\n  padding-right  : 3px;\n  padding-bottom : 3px;\n  padding-left   : 3px;\n}\ndiv.etext-box .boxcont = {\n  padding-top    : 3px;\n  padding-right  : 3px;\n  padding-bottom : 3px;\n  padding-left   : 3px;\n}\ndiv.etext-box span.boxhide {\n  display: none;\n  float: right;\n  font-size : xx-small;\n  color: blue;\n  cursor: pointer;\n}\ndiv.etext-box span.boxshow {\n  display: none;\n  float: right;\n  font-size : xx-small;\n  color: blue;\n  cursor: pointer;\n}\n\n\n/* extension-code */\ndiv.etext-code {\n  margin-left  : 5%;\n  margin-right : 5%;\n}\ndiv.etext-code .highlighttable td.linenos {\n  padding : 3px;\n  color : brown;\n  background-color : activeborder;\n}\ndiv.etext-code .highlighttable td.code {\n  padding : 3px\n}\ndiv.etext-code .highlight {\n  background-color : #FAFAFA;\n}\ndiv.etext-code .codecont {\n  background : #FAFAFA;\n  border : 1px dashed gray;\n}\n\n/* extension-footnote */\ndiv.etext-footnote .footnote {\n}\ndiv.etext-footnote table {\n  margin-left: 5px;\n}\ndiv.etext-footnote td.anchor {\n  padding: 5px;\n  color: blue;\n  vertical-align: top;\n}\ndiv.etext-footnote td.notes {\n  padding: 5px;\n  text-align: left;\n}\n\n/* extension-html */\ndiv.etext-html .html {\n}\n\n/* extension-nested */\ndiv.etext-nested .nested {\n}\n\n/* Templated tags */\nspan.etttag.pre {\n  white-space : pre;\n  font-family : monospace;\n}\nabbr.etttag {\n}\nspan.etttag.fixme {\n  border : 1px solid cadetBlue;\n  color : red;\n  padding: 1px;\n  font-family : monospace;\n}\ndiv.etttag.qbq {\n  font-style : italic;\n  margin : 5px 0px 5px 0px;\n  padding : 15px 0px 10px 40px;\n  width: 70%;\n  white-space: pre;\n}\nspan.etttag.smile {\n  font-size: x-large;\n  color: darkOrchid;\n  padding: 1px;\n  font-family : monospace;\n}\nspan.etttag.sad {\n  font-size: x-large;\n  color: orangeRed;\n  padding: 1px;\n  font-family : monospace;\n}\naddress.etttag {\n}\nspan.etttag.fnt {\n}\nsup.etttag.footnote {\n}\nsup.etttag.footnote a {\n  text-decoration: none;\n}\n </style>', '<h1 class="etsec" style="">', u' ', u'heading', u'<a id=" heading"></a>', u'<a class="etseclink" href="# heading" title="Link to this section">&#9875;</a>', u'\n', '</h1>\n', u'\n', '<p class="ettext">\n', u'In', u' ', u'~', '<em class="etmark" style="">', u' ', u'1862', u' ', '</em>', u',', u' ', u'~', u' ', '<strong class="etmark" style="">', u'Charles', u' ', u'Lutwidge', u' ', u'Dodgson', '</strong>', u',', u' ', u'a', u' ', '<u class="etmark" style="">', u'shy', u' ', u'Oxford', u' ', u'mathematician', u' ', u'~', u'\n', u'with', '</u>', u' ', u'a', u' ', u'stammer', u',', u' ', '<em><u class="etmark" style="">', u'created', '</u></em>', u' ', u'a', u' ', '<em><u class="etmark" style="">', u'story', '</u></em>', u' ', '<strong><em class="etmark" style="">', u'about', '</em></strong>', u' ', u'a', u' ', '<strong><em class="etmark" style="">', u'little', u' ', u'girl', u'\n', u'tubling', '</em></strong>', u' ', '<strong><u class="etmark" style="">', u'down', '</u></strong>', u' ', '<strong><u class="etmark" style="">', u'a', u' ', '</u></strong>', u' ', u'rabbit', u' ', u'hole.', u' ', u'subscript', u' ', u'as', u' ', u'log', '<sub class="etmark" style="">', u'2', '</sub>', u' ', u'superscript', u'\n', u'x', '<sup class="etmark" style="">', u'2', '</sup>', u'.', u'\n', '</p>\n', u'\n', '<p class="ettext">\n', '<strong><em><u class="etmark" style="">', u'Thus', u' ', u'geban', u' ', u'the', u' ', u'immortal', u' ', u"'", u'^', u' ', u'adventures', u' ', u'/', u' ', u'of', u' ', u'Alice', u',', u' ', '</u></em></strong>', u' ', u'perhaps', u' ', u'the', u' ', u'most', u' ', u'popular', u'\n', u'heroine', u' ', u'_', u' ', u'in', u' ', u',', u' ', u'English', u' ', u'`', u' ', u'literature', u' ', u'.', u'\n', u'charm', u' ', u'[', u' ', u'of', u' ', u']', u' ', u'{', u' ', u'the', u' ', u'}', u' ', u'Alice', u' ', u'&lt;', u' ', u'books', u'-', u'with', u' ', u'&gt;', u' ', u'those', u' ', u'wonderfully', u' ', u'eccentric', u' ', u'characters.', u'\n', u'google', u' ', u'website', u' ', u':', u' ', u'<a class="etwwwuri" href="www.google.com">www.google.com</a>', u' ', u'to', u' ', u'search', u'\n', u'pluggdapps', u' ', u'website', u' ', u':', u' ', u'<a class="ethttpsuri" href="https://pluggdapps.com">https://pluggdapps.com</a>', u' ', u'to', u' ', u'develop', u'\n', '</p>\n', u'\n', '<hr class="ethorz"/>\n', u'\n', u'\n', '<h3 class="etsec" style="">', u' ', u'small', u' ', u'heading', u'<a id=" small heading"></a>', u'<a class="etseclink" href="# small heading" title="Link to this section">&#9875;</a>', u'\n', '</h3>\n', '<p class="ettext">\n', u'link', u' ', u'is', u' ', u'<a class="etlink" target="" href="www.google.com">google.com</a>', u' ', u'and', u',', u'\n', u'macro', u' ', u'is', u' ', '<span class="etm-yearsbefore" style="color: red; fromyear: 2008">past 3 years, 7 months</span>', u' ', u'as', u' ', u'well', u',', u'\n', u'ok.', u' ', u'And', u' ', u'some', u' ', u'bit', u' ', u'of', u' ', u'HTML', u' ', u'as', u' ', u'well', u' ', u' <pre> So goes \nthe kite </pre> ', u'.', u'\n', '</p>\n', u'\n', '</article>', '</body></html>'] )
  return _m.popbuftext()

# ---- Footer

_etxhash = None
_etxfile = '/home/pratap/mybzr/pratap/dev/eazytext/eazytext/test/stdfiles/markuptext1.etx'
