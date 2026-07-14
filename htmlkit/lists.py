from markupsafe import Markup

def unordered_list(iterable, class_=None):
    open_tag = '<ul'
    if class_:
        open_tag += f' class="{class_}"'
    open_tag += '>'
    html = [open_tag]
    for obj in iterable:
        html.append(f'<li>{obj}</li>')
    html.append('</ul>')
    return Markup(''.join(html))

def definition_list(obj, class_=None):
    open_tag = '<dl'
    if class_:
        open_tag += f' class="{class_}"'
    open_tag += '>'
    html = [open_tag]
    for key, value in obj.items():
        html.append(f'<dd>{key}</dd>')
        if isinstance(value, dict):
            value = definition_list(value, class_=class_)
        html.append(f'<dt>{value}</dt>')
    html.append('</dl>')
    return Markup(''.join(html))
