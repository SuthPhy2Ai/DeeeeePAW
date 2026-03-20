project = 'DeePAW'
copyright = '2024-2026, DeePAW Team'
author = 'DeePAW Team'
release = '2.2.0'

# Sphinx extensions (intl is built-in in Sphinx 9.x)
extensions = []

templates_path = ['_templates']
exclude_patterns = []

# Internationalization settings
# Default language (English)
language = 'en'

# Supported languages
locale_dirs = ['locale']  # Directory for translation files
gettext_compact = False   # Keep separate .pot files for each document

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['language-switcher.css']
html_js_files = ['language-switcher.js']
html_theme_options = {
    'navigation_depth': 3,
    'collapse_navigation': False,
}
