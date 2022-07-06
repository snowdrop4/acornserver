#!/bin/sh

git filter-branch --env-filter '
CORRECT_NAME="snowdrop4"
CORRECT_EMAIL="82846066+snowdrop4@users.noreply.github.com"

export GIT_COMMITTER_NAME="$CORRECT_NAME"
export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
export GIT_AUTHOR_NAME="$CORRECT_NAME"
export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
' --tag-name-filter cat -- --branches --tags
