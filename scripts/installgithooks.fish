#!/usr/bin/env fish

set root (dirname (status --current-filename))

cp -r $root/githooks/ $root/../.git/hooks/
