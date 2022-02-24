# Run this file on main branch with a gh-pages worktree
from logging import warning
import sys
import os
import glob
import json

################################################################################
# Insist on Python >= 3.6
if sys.version_info < (3,6):
    error('Python 3.6 or newer is required')

################################################################################
# Iterate over all reports
FILES = []
for FILE in glob.glob('reports/**/*.txt', recursive=True):
    FILES.append(FILE)

FILES.sort()
PKG_STATUS = {}

for FILE in FILES:
    PKG_STATUS[os.path.splitext(os.path.basename(FILE))[0]] = open(FILE).read().rstrip()

REPORT = {}
REPORT['pkgs'] = PKG_STATUS

DIR = 'gh-pages/_data'

if not os.path.isdir(DIR):
    os.mkdir(DIR)

REPORT['total'] = 0
REPORT['success'] = 0
REPORT['failure'] = 0
REPORT['cancelled'] = 0

for pkg, status in PKG_STATUS:
    REPORT['total'] += 1
    if status == 'success':
        REPORT['success'] += 1
    elif status == 'failure':
        REPORT['failure'] += 1
    elif status == 'cancelled':
        REPORT['cancelled'] += 1
    else:
        warning('Unknown job status \"'+status+'\" for pkg \"'+pkg+'\"')

with open(DIR+'/report.json', 'w') as f:
    json.dumps(REPORT, f, indent=4)

relativeFailures = REPORT['failure'] / REPORT['total']
if relativeFailures > 0.05:
    color = 'red'
elif relativeFailures > 0:
    color = 'orange'
else:
    color = 'green'

BADGE = {
    'schemaVersion' : 1,
    'label': 'Tests',
    'message': '%d/%d passing' % (REPORT['success'], REPORT['total']),
    'color': color,
    'namedLogo': "github"
}

with open(DIR+'/badge.json', 'w') as f:
    json.dumps(BADGE, f, indent=4)