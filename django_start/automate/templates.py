from string import Template

# HTML Template for the index page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Django Start</title>
        <style>
            *{text-align: center}
            div{display:flex; justify-content:center}
        </style>
    </head>
    <body>
        <h1 style="text-align: center">Hello, Django-Start</h1>
        <a style="text-align: center" class="github-button" href="https://github.com/islam-kamel/django-start" data-color-scheme="no-preference: light; light: light; dark: dark;" data-size="large" data-show-count="true" aria-label="Star islam-kamel/django-start on GitHub">Django-Start</a>
    </body>
    <script async defer src="https://buttons.github.io/buttons.js"></script>
</html>
"""

# View function template
VIEW_FUNC_TEMPLATE = Template("""
from django.shortcuts import render

def index(request):
    return render(request, "$render_path")
""")
