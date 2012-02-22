#!/usr/bin/env python

from optparse import OptionParser
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
from html2text import html2text

import urllib2
import re
import htmlentitydefs

id_prefix = ''

def main():
    parser = OptionParser()
    parser.add_option('-p', '--prefix')

    options, args = parser.parse_args()
    
    global id_prefix
    id_prefix = options.prefix or ''
    
    if len(args) == 0:
        print 'error: Specify a URL'
        return
    if len(args) > 1:
        print 'error: Can only accept one argument'
        return
    
    url = args[0]
    
    # If the url does not start with http:// or https:// then assume http://
    if not url.startswith('http'):
        url = 'http://%s' % url
    
    print scrape_url(url)

def scrape_url(url, id_prefix=''):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    
    div = soup.find('div', {'class': 'articlebody'})
    
    # Ensure the target element has been found
    if div is None:
        print 'error: Could not find target element'
        return
    
    sections = []
    for item in div:
        if isinstance(item, Tag):
            sections.append(convert_tag(item))
        elif isinstance(item, NavigableString):
            pass
    
    return '\n\n'.join(sections)

def isheader(tag_name):
    return re.match('h[1-6]', tag_name) is not None

def convert_tag(tag):
    if tag.name == 'p':
        text = html2text(str(tag)).rstrip()
        return paragraph_to_list_item(text)
        
    elif isheader(tag.name):
        return '<%(tag)s id="%(id)s">%(title)s</%(tag)s>' % {
            'tag': tag.name,
            'id': id_prefix + string_to_id(html2text(tag.string).rstrip()),
            'title': html2text(tag.string).rstrip(),
        }
    elif tag.name == 'ul':
        return html2text(str(tag)).rstrip()
    
    return tag


def string_to_id(title):
    return title.lower().replace(' ', '-')

def paragraph_to_list_item(string):
    
    output_lines = []
    
    for line in string.split('\n\n'):
        clean_line = re.sub('\n', ' ', line).strip()
        if re.match('[0-9]+\.\ ', clean_line) is not None:
            output_lines.append('\n%s' % clean_line)
        elif re.match('[a-z]+\.\ ', line) is not None:
            output_lines.append(re.sub('^[a-z]+\.', '\n    1.', clean_line))
        else:
            output_lines.append(clean_line)
    
    return '\n\n'.join(output_lines)

if __name__ == '__main__':
    main()