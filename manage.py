
import os, sys, re
import subprocess
import sys
from flask_script import Manager

# TODO Change this to import from your main application file
import myapp as app_module
app = app_module.app


if hasattr(app_module, 'manager'):
    manager = app_module.manager
else:
    manager = Manager(app)

_status_re = re.compile('^(.)(.) (.*)')

@manager.command
def initdb():
    if hasattr(app_module, 'db'):
        db = app_module.db
    elif 'init' in sys.modules and hasattr(sys.modules['init'], 'db'):
        db = sys.modules['init'].db
    else:
        raise RuntimeError('cannot find database object')

    print('initializing database')
    db.create_all(app=app)

@manager.command
def package(output_file = 'submission.zip', force=False):
    """Prepares a package for assignment submission."""
    print('checking repository status')
    os.chdir(app.root_path)
    if os.path.exists('__init__.py'):
        print('found __init__.py, assuming in package')
        os.chdir('..')
    if not os.path.exists('manage.py'):
        print('manage.py not found, something is likely wrong',
              file=sys.stderr)
    if not os.path.exists('.git'):
        if not force:
            print("this doesn't look like a Git repository, bailing",
                  file=sys.stderr)
            print("use --force to override", file=sys.stderr)
            sys.exit(1)
        else:
            print("this doesn't look like a Git repository, continuing anyway",
                  file=sys.stderr)
    proc = subprocess.Popen(['git', 'status', '--porcelain'], stdout=subprocess.PIPE)
    with proc.stdout:
        bad = False
        for line in proc.stdout:
            match = _status_re.match(line.decode())
            if not match:
                continue
            file = match.group(3)
            x = match.group(1)
            y = match.group(2)
            if x+y == '??':
                print('untracked file {}, did you mean to add?'.format(file),
                      file=sys.stderr)
            else:
                print('uncommitted changes to {}'.format(file),
                      file=sys.stderr)
            bad = True
        if bad:
            if force:
                print('uncommitted changes (proceeding anyway)',
                      file=sys.stderr)
            else:
                print('uncommitted changes, cancelling (--force to proceed anyway)',
                      file=sys.stderr)
                sys.exit(2)

    app.logger.info('creating git archive')
    pfx, ext = os.path.splitext(os.path.basename(output_file))
    rc = subprocess.call(['git', 'archive', '--prefix={}/'.format(pfx),
                          '-o', output_file, 'HEAD'])
    if rc:
        print('git archive failed with code {}'.format(rc), file=sys.stderr)
        sys.exit(3)
    print('wrote archive to {}'.format(output_file))


@manager.command
def socketserver(debug=False, reload=False, port=5000, host='127.0.0.1'):
    if hasattr(app_module, 'io'):
        sio = app_module.io
        sio.run(app, debug=debug, use_reloader=reload, port=int(port), host=host)
    else:
        print('app does not define socketio, cannot run', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    manager.run()