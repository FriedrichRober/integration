# Run this file on main branch with a gh-pages worktree
from utils import *
import sys
import os
import glob
import json
from datetime import datetime

################################################################################
# Insist on Python >= 3.6
if sys.version_info < (3,6):
    error('Python 3.6 or newer is required')

if len(sys.argv) != 4:
    error('Unknown number of arguments')

docker = sys.argv[1]
hash = sys.argv[2]
branch = sys.argv[3]

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
REPORT['date'] = str(datetime.now())
REPORT['pkgs'] = PKG_STATUS

DIR_REPORT_BASE = 'gh-pages/_data/reports'
DIR_REPORT = DIR_REPORT_BASE+'/by_hash/'+hash
os.makedirs(DIR_REPORT, exist_ok = True)

REPORT['total'] = 0
REPORT['success'] = 0
REPORT['failure'] = 0
REPORT['cancelled'] = 0

for pkg, status in PKG_STATUS.items():
    REPORT['total'] += 1
    if status == 'success':
        REPORT['success'] += 1
    elif status == 'failure':
        REPORT['failure'] += 1
    elif status == 'cancelled':
        REPORT['cancelled'] += 1
    else:
        warning('Unknown job status \"'+status+'\" for pkg \"'+pkg+'\"')

with open(DIR_REPORT+'/report.json', 'w') as f:
    json.dump(REPORT, f, ensure_ascii=False, indent=4)

os.symlink(DIR_REPORT, DIR_REPORT_BASE+'/latest')

relativeFailures = 1 - REPORT['success'] / REPORT['total']
if relativeFailures > 0.05:
    color = 'critical'
elif relativeFailures > 0:
    color = 'important'
else:
    color = 'success'

DIR_BADGE = 'gh-pages/_data'

BADGE = {
    'schemaVersion' : 1,
    'label': 'Tests',
    'message': '%d/%d passing' % (REPORT['success'], REPORT['total']),
    'color': color,
    'namedLogo': "github"
}

with open(DIR_BADGE+'/badge.json', 'w') as f:
    json.dump(BADGE, f, ensure_ascii=False, indent=4)