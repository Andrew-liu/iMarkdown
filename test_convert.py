# -*- coding: utf-8 -*-
#!/usr/bin/env python


from iMarkdown import Convert

def test_convert():
    my_str = "hello world"
    c = Convert(my_str)
    text = c.zh2utf8()
    assert(isinstance(text, str) == True)
    c.zh2unicode()
    assert(isinstance(text, unicode) == True)
