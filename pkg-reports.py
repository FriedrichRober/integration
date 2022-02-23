import sys
import os
import glob
import json

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
REPORTS = {}

for FILE in FILES:
    REPORTS[os.path.splitext(os.path.basename(FILE))[0]] = open(FILE).read().rstrip()

print(json.dumps(REPORTS, indent=4))
