# Random Squid utilities, which don't need Sage, go here.

from html.parser import HTMLParser
import string
import random
import re
import os


def img_width2latex(text):
    r'''Convert html img attribute 'text' to format suitable for LaTeX.
    For example, if text = "40%"  (from <img width="40%" src="...">), output "0.4\textwidth"
    (for \includegraphics[width=0.4\textwidth]{...})'''
    if text[-1] == "%":
        return f'width={int(text[:-1])*0.01:.2f}\\textwidth'
    if text[-2:] == "px":
        return f'width={round(int(text[:-2])*0.75)}pt'
    return f'width={text}'

def img_height2latex(text):
    r'''Convert html img attribute 'text' to format suitable for LaTeX.
    For example, if text = "40%"  (from <img height="40%" src="...">), output "0.4\textheight"
    (for \includegraphics[height=0.4\textheight]{...})'''
    if text[-1] == "%":
        return f'height={int(text[:-1])*0.01:.2f}\\textheight'
    if text[-2:] == "px":
        return f'height={round(int(text[:-2])*0.75)}px'
    return f'height={text}'

def html2latex(text, verbose=False):
    '''
    Convert some html to latex.
    This will be used for Squid questions, so the html should be relatively simple.

    Implemented thus far:
      - <img>, with attributes height and width, either in px or %
      - <hr> <b> <i> <em> <u> <br> <p> <h1> <h2> <h3> <h4> <ol> <ul> <li> <a> <tt>

    To do:
      - tables   ... will require some sort of stack to count the number of columns, then go back and add the "lll"s
      - download and embed images if their src is a url?
      - <code>
      - Maybe do something interesting with comments?
    '''
    output = []  # list of strings, to be joined later
    # ignore_tags will be ignored, i.e. their tag name and attributes will be excluded:
    ignored_tags = ['td', 'tr', 'th', 'thead', 'table', 'head', 'body', 'meta', 'html', 'tbody', 'title', 'script',
                    'div', 'span', 'link', 'header', 'h5', 'style', 'font']
    class myparser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            nonlocal output  # we'll be modifying this as we go
            if tag == 'img':
                wh = []
                for key, value in attrs:
                    if key == 'src':
                        filename = value
                    if key == 'height':
                        wh.append(img_height2latex(value))
                    if key == 'width':
                        wh.append(img_width2latex(value))
                output.append(r'\includegraphics')
                if len(wh) > 0:
                    output.append('[' + ', '.join(wh) + ']')
                output.append('{' + filename + '}')
            elif tag == 'hr':
                output.append('\n' + r'\par\noindent\rule{\textwidth}{0.4pt}' + '\n')
            elif tag == 'b':
                output.append(r'{\bf ')
            elif tag == 'i':
                output.append(r'{\it ')
            elif tag == 'em':
                output.append(r'{\em ')
            elif tag == 'u':
                output.append(r'\underline{')
            elif tag == 'tt':
                output.append(r'\texttt{')
            elif tag == 'br':
                output.append('\n\n')
            elif tag == 'p':
                output.append('\n')
            elif tag == 'h1':
                output.append(r'{\Large\bf ')
            elif tag == 'h2':
                output.append(r'{\large\bf ')
            elif tag == 'h3':
                output.append(r'{\bf\it ')
            elif tag == 'h4':
                output.append(r'{\bf ')
            elif tag == 'ul':
                output.append(r'\begin{itemize}'+'\n')
            elif tag == 'ol':
                output.append(r'\begin{enumerate}'+'\n')
            elif tag == 'li':
                output.append(r'\item ')
            elif tag == 'a':
                for key, value in attrs:
                    if key == 'href':
                        target = value
                output.append(r'\href{'+target+'}{')
            elif tag in ignored_tags:
                pass   # we ignore these tags, since we don't want to typeset them
            else:      # a tag we don't know about, it might be math and not a tag at all, so let's do something with it
                unknown_tag = self.get_starttag_text()
                output.append('<'+html2latex(unknown_tag[1:]))  # if a valid tag closed this, then we want it processed!
                if verbose:
                    print(f'opening tag <{tag}> ignored. Exact text:')
                    print('  "'+unknown_tag+'"')



        def handle_endtag(self, tag):
            if tag in ['b', 'i', 'u', 'a', 'em','tt']:
                output.append('} ')
            elif tag in ['h1', 'h2', 'h3', 'h4']:
                output.append('}\n')
            elif tag in ['p', 'li']:
                output.append('\n')
            elif tag == 'ul':
                output.append(r'\end{itemize}'+'\n')
            elif tag == 'ol':
                output.append(r'\end{enumerate}'+'\n')
            elif tag in ignored_tags:
                pass   # we ignore these tags, since we don't want to typeset them
            else:
                output.append('</'+tag+'> ')   # some unknown tag, perhaps part of an equation...
                if verbose:
                    print(f'closing tag </{tag}> ignored.')

        def handle_data(self, data):
            output.append(data)

    parser = myparser()
    parser.feed(text)
    return ''.join(output)

def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    '''Returns a (cryptographically insecure!) random identifier of length size'''
    return ''.join(random.choice(chars) for _ in range(size))

# I need to extend the followinf get_img_filenames and qti_img_tags (and html2latex) so that it  can handle
# image sources which are urls.

def get_img_filenames(s):
    '''Returns a list of filenames mentioned in img tags in the string s.
    For now, assumes img src is a local file, not a url!'''
    return [m.group('filename') for m in re.finditer('<img\\s*src=(?P<quote>[\'"])(?P<filename>.*?)(?P=quote)', s)]

class MATHJAX():
    '''Takes an HTML formatted string with embedded LaTeX and typesets it. By Bjoern Rueffer'''
    def __init__(self,s):
        self.s = s
    def _repr_html_(self):
        '''this is used by display() / show() in your jupyter notebook'''
        return '''
        <div>
        <script type="text/javascript" async="" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML"></script>
        </div>''' + self.s
    def __str__(self):
        '''this is used by print() and str()'''
        return(self._repr_html_())

def get_filepaths(directory, one_up=False):
    ''' returns a list of all files under directory with paths relative to directory'''
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths

def get_subdirs(directory):
    '''returns a list of all subdirectories in directory'''
    dir_list = []
    for root, directories, files in os.walk(directory):
        for d in directories:
            dir_path = os.path.join(root, d)
            dir_list.append(dir_path)
    dir_list.reverse()
    return dir_list

def destroy(directory):
    '''DANGER! Recursively deletes everything in directory. Use with care.'''
    for filepath in get_filepaths(directory):
        os.remove(filepath)
    # now delete the subdirectories
    for d in get_subdirs(directory):
        os.rmdir(d)
    # finally, delete directory itself, which should be empty at this stage:
    os.rmdir(directory)
