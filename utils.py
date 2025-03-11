import re


re_closing_tag = r"</([a-z][^\s=\/\\\>]*)\s*>"
re_comment = r"<!--.*?-->"
re_tag = (
    r"""(<([a-z][^\s=/\\]*)(\s*[^\s=]+(\s*=\s*(\"|\').*?\5))*\s*(\/?)>)"""
    + ("|(%s)" % re_closing_tag)
    + ("|(%s)" % re_comment)
)


def get_end_index(file_content, start, elements=None, stop_at_close_error=False):
    if elements is not None and len(elements) == 0 and not stop_at_close_error:
        return start

    elements = elements or ()

    el = re.search(re_tag, file_content[start:], re.IGNORECASE | re.DOTALL)
    if not el:
        return None

    start += el.end()

    is_comment = el.group(9)
    if is_comment:
        return get_end_index(file_content, start, elements, stop_at_close_error)

    is_closing_tag = el.group(7)
    if is_closing_tag:
        tag_name = el.group(8).lower()
        try:
            ri = elements[::-1].index(tag_name.lower())
        except ValueError:
            ri = -1
        if ri >= 0:
            elements = elements[: -ri - 1]
        elif stop_at_close_error:
            return start
        return get_end_index(file_content, start, elements, stop_at_close_error)

    tag_name = el.group(2)
    is_self_closing = bool(el.group(6))
    if not is_self_closing:
        elements += (tag_name.lower(),)
    elif not elements:
        return None

    return get_end_index(file_content, start, elements, stop_at_close_error)


def get_start_index(file_content, end, elements=None):
    if elements is not None and not elements:
        return end

    elements = elements or ()

    el = list(re.finditer(re_tag, file_content[:end], re.IGNORECASE | re.DOTALL))[-1]
    if not el:
        return None

    end = el.start()

    is_comment = el.group(9)
    if is_comment:
        return get_start_index(file_content, end, elements)

    is_self_closing = bool(el.group(6))
    is_closing_tag = el.group(7)
    if is_self_closing:
        if not elements:
            return None
        return get_start_index(file_content, end, elements)

    if is_closing_tag:
        tag_name = el.group(8).lower()
        elements += (tag_name.lower(),)
        return get_start_index(file_content, end, elements)

    tag_name = el.group(2)
    try:
        ri = elements[::-1].index(tag_name.lower())
    except ValueError:
        ri = -1
    if ri >= 0:
        elements = elements[: -ri - 1]
    return get_start_index(file_content, end, elements)


if __name__ == "__main__":
    data = """<html lang="en">
    <body class="" data-transports="[&quot;polling&quot;,&quot;websocket&quot;]">
        <div id="app"></div>

        <!-- This is a comment -->
        <div>
            <div class="w<i/>ndow" sarst bim a='arst"' testtt="" a = "'aa

            aa"  >
                <div id="loading-status-container">
                    <img src="img/logo-vertical-transparent-bg.svg" class="logo" alt="" width="256" height="170">
                    <img src="xxx/logo-vertical-transparent-bg-inverted.svg" class="logo-inverted" alt="" width='25' height="170"/>
                    <br/>
                    <p id="loading-page-message">The Lounge requires a modern browser with JavaSc < ript enabled.</p>
                </div>
                <div id="loading-reload-container">
                    <p id="loading-slow">This is taking longer than it should, there might be connectivity issues.</p>
                    <button id="loading-reload" class="btn">Reload page</button>
                </div>
            </div>
        </div>
        <!-- Trap </body> -->
    </body>
</html>
"""

    # Test find closing
    assert get_end_index(data, data.index('<div class="w')) == 1030
    assert get_end_index(data, data.index('<p id="loading-slow"')) == 907
    assert get_end_index(data, data.index('<div id="app">')) == 127
    assert get_end_index(data, data.index("<body")) == 1087
    assert get_end_index(data, data.index("<br")) is None
    assert get_end_index(data, data.index('<img src="xxx')) is None

    # Test find opening
    idx = get_start_index(data, data.index("</button>") + len("</button>"))
    assert data[idx:].startswith("<button")
    assert idx == 928

    idx = get_start_index(data, data.index("<!-- Trap") - 2)
    assert data[idx:].startswith("<div>")
    assert idx == 172

    idx = get_start_index(data, data.index("<!-- This is a comment") - 2)
    assert data[idx:].startswith('<div id="app">')
    assert idx == 107

    assert get_start_index(data, data.index("<br/>") + len("<br/>")) is None
    assert get_start_index(data, data.index("<br/>") + len("<br/>")) is None

    idx = get_start_index(data, data.index("issues.</p>") + len("</p>"))
    assert data[idx:].startswith('<p id="loading-slow">')
    assert idx == 809

    print("OK")
