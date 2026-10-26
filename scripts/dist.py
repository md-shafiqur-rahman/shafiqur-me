"""Copy the publishable site into dist/ for Vercel, leaving out source and tooling."""
import os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist')
SKIP = {'dist', 'node_modules', 'content', 'scripts', 'tina', '.git', '.github', '.vercel',
        'package.json', 'package-lock.json', 'README.md', 'vercel.json', '.gitignore', '.DS_Store'}

shutil.rmtree(DIST, ignore_errors=True)
os.makedirs(DIST)
for name in os.listdir(ROOT):
    if name in SKIP:
        continue
    src, dst = os.path.join(ROOT, name), os.path.join(DIST, name)
    if os.path.isdir(src):
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns('.DS_Store'))
    else:
        shutil.copy2(src, dst)
print('dist ready:', sorted(os.listdir(DIST)))
