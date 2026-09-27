"""
Script to apply the original layout/theme to main.py
"""
import os

with open('frontend/main.py', 'r', encoding='utf-8') as f:
    main_text = f.read()

with open('frontend/main_orig_clean.py', 'r', encoding='utf-8-sig') as f:
    orig_text = f.read()

# 1. Extract and replace CSS
css_start = orig_text.find('st.markdown("""\n<style>')
css_end = orig_text.find('</style>\n""", unsafe_allow_html=True)') + len('</style>\n""", unsafe_allow_html=True)')
orig_css = orig_text[css_start:css_end]

main_css_start = main_text.find('st.markdown("""\n<style>')
main_css_end = main_text.find('</style>\n""", unsafe_allow_html=True)') + len('</style>\n""", unsafe_allow_html=True)')

# 2. Extract and replace Auth HTML Block
auth_start = orig_text.find('# ==========================================\n# AUTH PORTAL (LOGIN / REGISTER)')
nav_start = orig_text.find('# ==========================================\n# MAIN NAVIGATION (Replaced Sidebar)')
orig_auth = orig_text[auth_start:nav_start]

main_auth_start = main_text.find('# ==========================================\n# AUTH PORTAL (LOGIN / REGISTER)')
main_nav_start = main_text.find('# ==========================================\n# MAIN NAVIGATION (Replaced Sidebar)')

# Assemble new main.py
new_main = main_text[:main_css_start] + orig_css + main_text[main_css_end:main_auth_start] + orig_auth + main_text[main_nav_start:]

with open('frontend/main.py', 'w', encoding='utf-8') as f:
    f.write(new_main)
print("Applied Original Theme & Auth HTML successfully!")
