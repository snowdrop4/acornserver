import sys

from isort.hooks import git_hook

sys.exit(git_hook(strict=True, modify=True, lazy=True))
