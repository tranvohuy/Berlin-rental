import immo


def test_urlquery():
    html = immo.urlquery("http://www.randomtextgenerator.com/")
    # print(type(html))

    assert isinstance(html, bytes)
