
import os

def emBacktick(txt):
    """Change any emphasised text to html with <em> tags.

        Recursive."""

    html = ''

    emPosn = txt.find(' `')
    if txt.startswith('`'):
        emPosn = 0

    if  emPosn >= 0:
        # has backtick
        emEnd = txt.find('`', emPosn + 2)
        if emEnd == -1:
            raise ValueError('Unpaired `\n')
        else:
            text = txt[emPosn + 1:emEnd].strip('`').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html += txt[:emPosn]
            html += ' <code>{:s}</code>'.format(text)
            html += txt[emEnd + 1:]
            html = emBacktick(html) # recursive call
    else:
        html = txt

    return html

def emStrong(txt):
    """Change any strong emphasised text to html with <strong> tags.

        Recursive."""

    html = ''

    strongPosn = txt.find('**')
    if txt.startswith('**'):
        strongPosn = 0

    if  strongPosn >=0:
        # has strong emphasis
        strongEnd = txt.find('**', strongPosn + 2)
        if strongEnd == -1:
            return txt
            #raise ValueError('Unpaired **')
        else:
            strongText = txt[strongPosn:strongEnd].strip('**')
            html += txt[:strongPosn]
            html += '<strong>{:s}</strong>'.format(strongText)
            html += txt[strongEnd + 2:]
            html = emStrong(html) # recursive call
    else:
        html = txt

    return html

def emNormal(txt):
    """Change any emphasised text to html with <em> tags.

        Recursive."""

    html = ''

    emPosn = txt.find('*')
    if txt.startswith('*'):
        emPosn = 0

    if  emPosn >=0:
        # has emphasis
        emEnd = txt.find('*', emPosn + 1)
        if emEnd == -1:
            return txt
            #raise ValueError('Unpaired *')
        else:
            text = txt[emPosn:emEnd].strip('*')
            html += txt[:emPosn]
            html += '<em>{:s}</em>'.format(text)
            html += txt[emEnd + 1:]
            html = emNormal(html) # recursive call
    else:
        html = txt

    return html

def emStrongUnderscore(txt):
    """Change any strong emphasised by underscore text to html with <strong> tags.

        Recursive."""

    html = ''

    strongPosn = txt.find(' __')
    if txt.startswith('__'):
        strongPosn = 0

    if  strongPosn >= 0:
        # has strong emphasis
        strongEnd = txt.find('__', strongPosn + 3)
        if strongEnd == -1:
            raise ValueError('Unpaired __')
        else:
            strongText = txt[strongPosn + 1:strongEnd].strip('__')  #.lstrip('__').rstrip('__')
            html += txt[:strongPosn]
            html += ' <strong>{:s}</strong>'.format(strongText)
            html += txt[strongEnd + 2:]
            html = emStrongUnderscore(html) # recursive call
    else:
        html = txt

    return html

def emNormalUnderscore(txt):
    """Change any emphasised by underscore text to html with <em> tags.

        Recursive."""

    html = ''

    emPosn = txt.find(' _')
    if txt.startswith('_'):
        emPosn = 0

    if  emPosn >= 0:
        # has emphasis
        emEnd = txt.find('_', emPosn + 2)
        if emEnd == -1:
            raise ValueError('Unpaired _')
        else:
            text = txt[emPosn + 1:emEnd].strip('_')
            html += txt[:emPosn]
            html += ' <em>{:s}</em>'.format(text)
            html += txt[emEnd + 1:]
            html = emNormalUnderscore(html) # recursive call
    else:
        html = txt

    return html

def em(txt):
    """Change any emphasised or strong text to html.
        returns :html:string: the text with html emaphsis tags."""

    newText = txt.replace('&', '&amp;')

    try:
        newText = emBacktick(newText)
        newText = emStrongUnderscore(newText)
        newText = emNormalUnderscore(newText)

        newText = emStrong(newText)
        html = emNormal(newText)
    except ValueError as e:
        html = str(e)

    return html


class ToHtml(object):
    """Converts  a subset of Markdowmn to html."""

    def __init__(self, header=''):

        """Constructor for ToHtml."""

        self.header = header

    def convert(self, mdText):

        """Converts markdown text to html.

            :md:string: the markdown text to convert

            returns :html:string: the converted html
            """

        # Initial values
        blank = True
        paragraph = False
        listItem = False
        listItemOrdered = False
        codeBlock = False

        # build html header<!DOCTYPE html>
        self.html = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html>
<head><meta charset="utf-8"/>'''

        self.html += self.header + '''
</head>
<body>
'''

        self.mdLines = mdText.split('\n')

        for line in self.mdLines:

            if line.startswith('######'): # header 6

                header = line.lstrip('#').strip()
                self.html += '<h6>{:s}</h6>\n'.format(em(header))
                blank = True

            elif line.startswith('#####'): # header 5

                header = line.lstrip('#').strip()
                self.html += '<h5>{:s}</h5>\n'.format(em(header))
                blank = True

            elif line.startswith('####'): # header 4

                header = line.lstrip('#').strip()
                self.html += '<h4>{:s}</h4>\n'.format(em(header))
                blank = True

            elif line.startswith('###'): # header 3

                header = line.lstrip('#').strip()
                self.html += '<h3>{:s}</h3>\n'.format(em(header))
                blank = True

            elif line.startswith('##'): # header 2

                header = line.lstrip('#').strip()
                self.html += '<h2>{:s}</h2>\n'.format(em(header))
                blank = True

            elif line.startswith('#'): # header 1

                header = line.lstrip('#').strip()
                self.html += '<h1>{:s}</h1>\n'.format(em(header))
                blank = True

            elif line.startswith(('- ', '+ ', '* ')): # unordered list
                if blank:
                    self.html += '<ul>\n<li>{:s}</li>\n'.format(em(line.lstrip('-+*').strip()))
                    listItem = True
                    blank = False
                else:
                    self.html += '<li>{:s}</li>\n'.format(em(line.lstrip('-+*').strip()))
                    listItem = True

            elif line.startswith('1. '): # ordered list
                if blank:
                    self.html += '<ol>\n<li>{:s}</li>\n'.format(em(line.lstrip('1.').strip()))
                    listItemOrdered = True
                    blank = False
                else:
                    self.html += '<li>{:s}</li>\n'.format(em(line.lstrip('1.').strip()))
                    listItemOrdered = True

            elif line.startswith(('\t')): # code block with tab
                if blank:
                    self.html += '<pre><code>{:s}\n'.format(line[1:].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
                    codeBlock = True
                    blank = False
                else:
                    self.html += '{:s}\n'.format(line[1:].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
                    codeBlock = True

            elif line.startswith(('---', '***', '___')): # horizontal rule
                self.html += '<hr />'
                blank = True

            elif line.startswith(('    ')): # code block with 4 spaces
                if blank:
                    self.html += '<pre><code>{:s}\n'.format(line[4:].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
                    codeBlock = True
                    blank = False
                else:
                    self.html += '{:s}\n'.format(line[4:].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
                    codeBlock = True

            elif line.startswith(('!')): # image
                fileName = line.split('(')[1].rstrip(')')
                self.html += '<p><img src="{:s}" /></p>\n'.format(fileName.strip())
                blank = True

            elif line.startswith(('[')): # link
                params = line.split(']')
                url = params[1].rstrip(')').lstrip('(')
                linkText = params[0].lstrip('[')
                self.html += '<p><a href="{:s}">{:s}</a></p>\n'.format(url, linkText)
                blank = True

            elif line.strip() == '': # Blank line
                blank = True

                # Add appropriate close tags
                if paragraph:
                    self.html = self.html.rstrip(' ')
                    self.html += '</p>\n'
                    paragraph = False
                if listItem:
                    self.html += '</ul>\n'
                    listItem = False
                if listItemOrdered:
                    self.html += '</ol>\n'
                    listItemOrdered = False
                if codeBlock:
                    self.html += '</code></pre>\n'
                    codeBlock = False

            else: # Default: paragraph text
                if blank:
                    self.html += '<p>'
                    paragraph = True
                    blank = False
                self.html += em(line.lstrip()) + ' '

        self.html += '</body>'

        return self.html