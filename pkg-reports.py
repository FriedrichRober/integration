import sys
import os
import glob
import pprint

################################################################################
# Insist on Python >= 3.6
if sys.version_info < (3,6):
    error("Python 3.6 or newer is required")

################################################################################
# Iterate over all reports
FILES = []
for FILE in glob.glob('reports/**/*.txt', recursive=True):
    FILES.append(FILE)

FILES.sort()
REPORTS = []

for FILE in FILES:
    REPORTS.append({
        "pkg": os.path.basename(FILE),
        "status": open(FILE).read().rstrip()
    })

pp = pprint.PrettyPrinter(depth=2)
pp.pprint(REPORTS)
