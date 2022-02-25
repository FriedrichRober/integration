# Run this file on main branch with data and gh-pages worktree
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
DIR_LATEST_REPORT = os.readlink(DIR_LATEST_REPORT_SYMBOLIC)

with open(DIR_LATEST_REPORT+'/report.json', 'r') as f:
    LAST_REPORT = json.load(f)

with open(DIR_REPORT+'/report.md', 'w') as f:
    # Header
    f.write('# Package Evaluation Report\n\n')
    f.write('## Job Properties\n\n')
    f.write('*Commit(s):* %s\n\n' % hash)
    f.write('*Triggered By:*\n\n')
    f.write('In total, %d packages were tested, out of which %d succeeded, %d failed and %d were skipped.\n\n' % (REPORT['total'], REPORT['success'], REPORT['failure'], REPORT['cancelled']))

    PKGS = REPORT['pkgs']
    LAST_PKGS = LAST_REPORT['pkgs']

    ############################################################################
    # New Packages
    PKGS_NEW = [pkg for pkg in PKGS.keys() if
        not pkg in LAST_PKGS.keys()]

    if len(PKGS_NEW) > 0:
        f.write('## New Packages\n\n')
        for pkg in PKGS_NEW:
            status = PKGS_NEW[pkg]
            f.write('%s : %s <br>\n' % (pkg, status))

    ############################################################################
    # Removed Packages
    PKGS_REMOVED = [pkg for pkg in LAST_PKGS.keys() if
        not pkg in PKGS.keys()]

    if len(PKGS_REMOVED) > 0:
        f.write('## Removed Packages\n\n')
        for pkg in PKGS_REMOVED:
            status = PKGS_REMOVED[pkg]
            f.write('%s : %s <br>\n' % (pkg, status))

    ############################################################################
    # Changed Status Packages
    for STATUS, STATUS_MSG in [('failure', 'failed'),
                               ('success', 'succeeded'),
                               ('cancelled', 'cancelled')]:
        PKGS_NOW_CHANGED = [pkg for pkg in PKGS.keys() if
            pkg in LAST_PKGS.keys() and
            PKGS[pkg] != LAST_PKGS[pkg] and
            PKGS[pkg] == STATUS]

        if len(PKGS_NOW_CHANGED) > 0:
            f.write('## Packages now failing\n\n')
            f.write('%d packages %s tests only on the current version.' % (len(PKGS_NOW_CHANGED), STATUS_MSG))
            f.write('<details> <summary>Click to expand!</summary>\n')
            for pkg in PKGS_NOW_CHANGED:
                status = PKGS[pkg]
                last_status = LAST_PKGS[pkg]
                f.write('%s : changed status from %s to %s <br>\n' % (pkg, last_status, status))
            f.write('</details>\n\n')

    ############################################################################
    # Same Status Packages
    for STATUS, STATUS_MSG in [('failure', 'failed'),
                               ('success', 'succeeded'),
                               ('cancelled', 'cancelled')]:
        PKGS_FILTERED = [pkg for pkg in PKGS.keys() if
            pkg in LAST_PKGS.keys() and
            PKGS[pkg] == LAST_PKGS[pkg] and
            PKGS[pkg] == STATUS]

        if len(PKGS_FILTERED) > 0:
            f.write('## Packages now failing\n\n')
            f.write('%d packages %s tests also on the previous version.' % (len(PKGS_FILTERED), STATUS_MSG))
            f.write('<details> <summary>Click to expand!</summary>\n')
            for pkg in PKGS_FILTERED:
                status = PKGS[pkg]
                f.write('%s : %s <br>\n' % (pkg, status))
            f.write('</details>\n\n')

symlink(DIR_REPORT, DIR_LATEST_REPORT_SYMBOLIC, overwrite=True)

################################################################################
# Generate html redirect
REPO = 'https://github.com/FriedrichRober/integration/blob'
with open('gh-pages/index.html', 'w') as f:
    f.write('''
    <!DOCTYPE html>
    <meta charset="utf-8">
    <title>Redirecting to latest report</title>
    <meta http-equiv="refresh" content="0; URL=%s">
    <link rel="canonical" href="%s">
    ''' % (REPO+'/'+DIR_REPORT+'/report.md', REPO+'/'+DIR_REPORT+'/report.md'))

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