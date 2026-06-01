from markupsafe import Markup

def unordered_list(iterable):
    html = ['<ul>']
    for obj in iterable:
        html.append(f'<li>{obj}</li>')
    html.append('</ul>')
    return Markup(''.join(html))
