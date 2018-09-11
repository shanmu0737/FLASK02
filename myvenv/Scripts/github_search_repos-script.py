#!F:\VIP\FLASK02\myvenv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'github2==0.6.2','console_scripts','github_search_repos'
__requires__ = 'github2==0.6.2'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('github2==0.6.2', 'console_scripts', 'github_search_repos')()
    )
