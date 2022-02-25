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
# Generate report
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

DIR_REPORT_BASE = 'data/reports'
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

################################################################################
# Generate markdown
DIR_LATEST_REPORT_SYMBOLIC = DIR_REPORT_BASE+'/latest'
# DIR_LATEST_REPORT = os.readlink(DIR_LATEST_REPORT_SYMBOLIC)

# with open(DIR_LATEST_REPORT+'/report.json', 'r') as f:
#     LAST_REPORT = json.load(f)

# with open('report.md', 'w') as f:
#     # Header
#     f.write('# Package Evaluation Report\n')
#     f.write('## Job Properties\n')
#     f.write('*Commit(s):*\n')
#     f.write('*Triggered By:*\n')
#     f.write('In total, %d packages were tested, out of which %d succeeded, %d failed and %d were skipped.' % (REPORT['total'], REPORT['success'], REPORT['failure'], REPORT['cancelled']))

#     # Failed tests
#     f.write('## :heavy_multiplication_x: Packages that failed tests\n')
#     f.write('**%d packages failed tests only on the current version.**\n' % REPORT['failure_current'])

#     f.write('<strong>%d packages failed tests on the previous version too.</strong>\n' % REPORT['failure_previous'])

#     # Skipped tests

#     # Successfull tests

symlink(DIR_REPORT, DIR_LATEST_REPORT_SYMBOLIC, overwrite=True)


################################################################################
# Generate badge

DIR_BADGE = 'data/badges'
os.makedirs(DIR_BADGE, exist_ok = True)

relativeFailures = 1 - REPORT['success'] / REPORT['total']
if relativeFailures > 0.05:
    color = 'critical'
elif relativeFailures > 0:
    color = 'important'
else:
    color = 'success'

BADGE = {
    'schemaVersion' : 1,
    'label': 'Tests',
    'message': '%d/%d passing' % (REPORT['success'], REPORT['total']),
    'color': color,
    'namedLogo': "github"
}

with open(DIR_BADGE+'/badge.json', 'w') as f:
    json.dump(BADGE, f, ensure_ascii=False, indent=4)