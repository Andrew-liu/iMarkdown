# -*- coding: utf-8 -*-
#!/usr/bin/env python

version = "1.0"
__author__ = "Andrew Liu"


'''
iMarkdown实现简单的markdown语法解析功能, 将markdown格式文本转换为HTML
文件, 并希望实现GFM(Github Feature Markdown)功能扩展模块, 其中主要实现
三个类, BasePattern类, Convert类, 核心iMarkdown类
'''

import re, sys

from logging import getLogger, StreamHandler, FileHandler, Formatter, \
                    DEBUG, INFO, WARN, ERROR, CRITICAL



### 简单的日志记录功能, 同时将日志输出到控制台和文件中 ###

MESSAGE_THRESHOLD = ERROR  # 设置控制台和文件的日志等级

logger = getLogger('MARKDOWN')
logger.setLevel(DEBUG)
formatter = Formatter('%(name)s-%(levelname)s: "%(message)s"')
console_handler = StreamHandler()
file_handler = FileHandler('log.txt')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
console_handler.setLevel(MESSAGE_THRESHOLD)
file_handler.setLevel(MESSAGE_THRESHOLD)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def message(level, text):
    ''' 对日志输入信息的简单封装'''
    logger.log(level, text)

### 文本类型转换类 ###
class Convert(object):
    """主要将所以编码的文本转换成unicode的编码或者utf-8编码 
    
    doc of class
    
    Attributess:
        text: 需要转换的文本字符串
    """
    def __init__(self, text=''):
        self.text = text

    def zh2utf8(self):
        """
        将utf8, gbk, big5, jp, kr编码的字符串转换为utf-8编码字符串
        """
        for c in ('utf-8', 'gbk', 'big5', 'jp',
            'euc_kr','utf16','utf32'):
            try:
                return self.text.decode(c).encode('utf-8')
            except:
                pass

    def zh2unicode(self):
        """
        将utf8, gbk, big5, jp, kr编码转换为unicode编码
        """

        for c in ('utf-8', 'gbk', 'big5', 'jp',
            'euc_kr','utf16','utf32'):
            try:
                return self.text.decode(c)
            except:
                pass

### 行内Pattern样式的正则匹配 ###

NOBRACKET = r'[^\]\[]*'
BRK = ( r'\[('
        + (NOBRACKET + r'(\[')*6
        + (NOBRACKET+ r'\])*')*6
        + NOBRACKET + r')\]' )
NOIMG = r'(?<!\!)'

BACKTICK_RE = r'\`([^\`]*)\`'                    # `e= m*c^2`
ESCAPE_RE = r'\\(.)'                             # \<
EMPHASIS_RE = r'\*([^\*]*)\*'                    # *emphasis*
STRONG_RE = r'\*\*(.*)\*\*'                      # **strong**
LINK_RE = NOIMG + BRK + r'\s*\(([^\)]*)\)'               # [text](url)
LINK_ANGLED_RE = NOIMG + BRK + r'\s*\(<([^\)]*)>\)'      # [text](<url>)
IMAGE_LINK_RE = r'\!' + BRK + r'\s*\(([^\)]*)\)' # ![alttxt](http://x.com/)
REFERENCE_RE = NOIMG + BRK+ r'\s*\[([^\]]*)\]'           # [Google][3]
IMAGE_REFERENCE_RE = r'\!' + BRK + '\s*\[([^\]]*)\]' # ![alt text][2]
NOT_STRONG_RE = r'( \* )'                        # stand-alone * or _
AUTOLINK_RE = r'<(http://[^>]*)>'                # <http://www.123.com>
AUTOMAIL_RE = r'<([^> \!]*@[^> ]*)>'               # <me@example.com>
HTML_RE = r'(\<[a-zA-Z/][^\>]*\>)'               # <...>

class BasePattern(object):
    """行内Pattern样式的正则匹配
    
    doc of class
    
    Attributess:
        pattern: 行内Pattern样式的正则表达式
    """
    def __init__ (self, pattern):
        self.pattern = pattern
        self.compiled_re = re.compile("^(.*)%s(.*)$" % pattern, re.DOTALL)

    def get_re_exp(self):
        return self.compiled_re

    def run(self, line):
        m = self.get_re_exp.match(line)
        if m:
            try:
                return m.group(1) + self.handle_match(m.group(2)) + m.group(3)
            except:
                message(ERROR, "process the pattern find a mistake! %" % line)
        else:
            return

    def handle_match(self, inline):
        pass  #子类集成重写

class BacktickPattern(BasePattern):
    # BACKTICK_RE = r'\`([^\`]*)\`'
    def __init__(self, pattern=BACKTICK_RE):
        BasePattern.__init__(self, pattern)

    def handle_match(self, inline):
        return '<code>' + ''.join(re.findall(r'[^\`]', inline)) + '<\code>'

class EmphasisPattern(BasePattern):
    #EMPHASIS_RE = r'\*([^\*]*)\*'
    def __init__(self, pattern=EMPHASIS_RE):
        BasePattern.__init__(self, pattern)

    def handle_match(self, inline):
        return '<em>' + ''.join(re.findall(r'[^*]', inline)) + '</em>'

class StrongPattern(BasePattern):
    #STRONG_RE = r'\*\*(.*)\*\*'
    def __init__(self, pattern=STRONG_RE):
        BasePattern.__init__(self, pattern)

    def handle_match(self, inline):
        return '<strong>' + ''.join(re.findall(r'[^**]', inline)) + '</strong>'

class LinkPattern(BasePattern):
    #LINK_RE = NOIMG + BRK + r'\s*\(([^\)]*)\)' 
    def __init__(self, pattern=LINK_RE):
        BasePattern.__init__(self, pattern)

    def handle_match(self, inline):
        m = re.match(r"\[(.*?)]\((.*?)\)", inline)
        if m:
            return '<a href="%s" title="%s" />' % (m.group(2), m.group(1))
        else:
            message(CRITICAL, "this %s tag make mistake" % inline)

class IMGPattern(BasePattern):
    #IMAGE_LINK_RE = r'\!' + BRK + r'\s*\(([^\)]*)\)'
    def __init__(self, pattern=IMAGE_LINK_RE):
        BasePattern.__init__(self, pattern)

    def handle_match(self, inline):
        m = re.match(r"!\[(.*?)]\((.*?)\)", inline)
        if m:
            return  '<img src="%s" title="%s" />' % (m.group(2), m.group(1))
        else:
            message(CRITICAL, "this %s tag make mistake" % inline)

### Pattern声明 ##
BACKTICK = BacktickPattern()
EMPHASIS = EmphasisPattern()
STRONG = StrongPattern()
LINK = LinkPattern()
IMG = IMGPattern()

### 核心类 ###
class iMarkdown(object):
    """核心类
    
    将markdown格式文本转换为HTML文本, 扫入一行, 转换<, 行内处理, 行头处理
    
    Attributess:
        
    """
    def ___init__(self, source=None, 
                  extensions=[],
                  extension_configs=None,
                  safe_mode=False):
        self.source = source
        if source == None:
            message(WARN, 'The source text is empty!')
        self.safe_mode = safe_mode
        self.registered_extensions = []
        self.header = ('<!DOCTYPE html><html><head><meta charset="utf-8" />'
                    '<title>An Markdown HTML</title></head><body>')
        self.footer = '</body></html>'
        self.inline_patterns = [BACKTICK,  # 五个类, 分别对类内标签进行处理
                                EMPHASIS, 
                                STRONG,
                                LINK,
                                IMG]
        self.change_patterns = [(r'\r\n|\r', '\n'), 
                                (r'&', '&amp;'),
                                (r'<', '&lt')]
        self.register_extensions(extensions = extensions, 
                                configs = extension_configs)
        self.body = ''
        self._transform()  # 核心转换函数
        self.html_page = self.header + self.body + self.footer

    def register_extensions(self, extensions, configs) :
        if not configs :
            configs = {}
        for ext in extensions :
            extension_module_name = 'ext_' + ext
            try:
                module = __import__(extension_module_name)
            except:
                message(CRITICAL, 
                    'couldn\'t load extension %s' % extension_module_name)
            else:
                if configs.has_key(ext):
                    configs_for_ext = configs[ext]
                else:
                    configs_for_ext = []
                extension = module.makeExtension(configs_for_ext)
                extension.extendMarkdown(self, globals)

    def _transform(self):
        # 1. 编码转换, 转换为unicode, 最后utf-8输出
        convert_code = Convert(self.source)
        self.source = convert_code.zh2unicode() #转换为unicode
        # 2. 文本特殊符号转换
        for (frm, to) in self.change_patterns :
            self.source = re.sub(frm, to, self.source)
        self.source += '\n\n'
        self.source = self.source.expandtabs(4)
        # 3. 按行划分source
        lines = self.source.split('\n')
        # 4. 扫描并缓存每一行, 并进行inline元素处理
        section = []  # 按块存储
        cache_line = ""
        for line in lines:
            line = self._process_inlinetag(line)
            # 5. 对整个section中block进行处理
            if line.startswith("#"):
                self._process_section(section)
                section = [line]
            elif (line.startswith('=') or line.startswith('--')) and cache_line != "":
                elf._process_section(line)
                section = [cache_line, line]
            else:
                section.append(line)
                cache_line = line
        self._processSection(section)

    def _process_section(self, section=''):
        '''块级元素按整个section进行处理'''
        # 缓存思想
        section_body = ""
        cache_line = ''
        for line in section:
            #先判断是不是ul, code, ol的最后一行
            section_body = self._process_last_line(line, cache_line, section_body)
            if line.startswith('#') or line.startswith('=') or line startswith('--'):
                section_body = self._process_head(line, cache_line, section_body)
            elif line.startswith('> '):
                section_body = self._process_quote(line, cache_line, section_body)
            elif line.startswith('\t') or line.startswith('    '):
                section_body = self._process_code(line, cache_line, section_body)
            elif re.compile(r'[ ]{0,3}[*+-]\s+(.*)').match(line)
                section_body = self._process_ullist(line, cache_line, section_body)
            elif re.compile(r'[ ]{0,3}[\d]*\.\s+(.*)').match(line):
                section_body = self._process_ollist(line, cache_line, section_body)
            else:
                section_body = self._process_text(line, cache_line, section_body)
            cache_line = line
        return section_body

    def _process_head(self, line='', cache_line='', section_body=''):
        if line.startswith('#'):
            m = re.compile(r'(#*)([^#]*)(#*)').match(line)
            if m:
                level = len(m.group(1))
                line = '<h%s>' % level + m.group(2) + '</h%s>' % level 
            else:
                message(CRITICAL, "we've got a problem header!")
        elif line.startswith('='):
            m = re.compile(r'(=+)').match(line)
            if m:
                line = '<h1>' + cache_line + '<\h1>'
            else:
                message(CRITICAL, "we've got a problem header!")
        elif line.startswith('--'):
            m = re.compile(r'(--+)').match(line)
            if m:
                line = '<h2>' + cache_line + '\h2'
            else:
                message(CRITICAL, "we've got a problem header!")
        section_body += line
        return section_body

    def _process_quote(self, line='', cache_line='', section_body=''):
        m = re.compile(r'> +(.*)').match(line)
        if m:
            line = '<blockquote>' + m.group(1) + '</blockquote>'
            section_body += line
            return section_body
        else:
            message(CRITICAL, "we've got a problem blockquote!")
        return section_body

    def _process_code(self, line='', cache_line='', section_body=''):
        # 通过判断缓存行格式
        line = re.sub('>', '&gt', line)  # 处理&, <, >
        if cache_line.startswith('\t') or cache_line.startswith('    '):
            #说明不是第一行代码
            section_body += line
        else:
            #第一行代码
            section_body += ('<pre><code>' + line)
        return section_body
        
    def _process_ullist(self, line='', cache_line='', section_body=''):
        line = re.sub('>', '&gt', line)
        if cache_line.startswith('- '):
            #说明不是第一行代码
            section_body += ('<li>' + m.group(1)+ '</li>')
        else:
            #第一行代码
            section_body += ('<ul><li>' + m.group(1) + '</li>')
        return section_body

    def _process_ollist(self, line='', cache_line='', section_body=''):
        line = re.sub('>', '&gt', line)
        m = re.compile(r'[ ]{0,3}[\d]*\.\s+(.*)').match(cache_line)
        if m:
            #说明不是第一行代码
            section_body += section_body += ('<li>' + m.group(1) + '</li>')
        else:
            #第一行代码
            section_body += ('<ol><li>' + m.group(1) + '</li>')
        return section_body 

    def _process_text(self, line='', cache_line='', section_body=''):
        line = re.sub('>', '&gt', line)
        section_body += ('<p>' + line + '</p>')

    def _process_last_line(self, line='', cache_line='', section_body=''):
        # 对最后一行代码判定添加闭合code, ul ol
        if (re.compile(r'((\t)|(    ))(.*)').match(cache_line) and not
            re.compile(r'((\t)|(    ))(.*)').match(line)):
            section_body += '</code></pre>'
        elif (re.compile(r'[ ]{0,3}[*+-]\s+(.*)').match(cache_line) and not 
            re.compile(r'[ ]{0,3}[*+-]\s+(.*)').match(line)):
            section_body += '</ul>'
        elif (re.compile('[ ]{0,3}[\d]*\.\s+(.*)').match(cache_line) and not
            re.compile('[ ]{0,3}[\d]*\.\s+(.*)').match(line)):
            section_body += '</ol>'
        else:
            return

    def _process_inlinetag(self, line, cache_line='', section_body=''):
        '''行内元素按行处理'''
        if len(line) <= 0:
            return None
        for inline_pattern in self.inline_patterns:
            line = inline_pattern.run(line)
        return line






