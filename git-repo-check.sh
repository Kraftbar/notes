#!/bin/bash

# Set the max depth for the search
max_depth=3
lock_file="/var/lock/git_repo_check/.git_repo_check.lock"

# Create the lock file directory if it doesn't exist
if [ ! -d "/var/lock/git_repo_check" ]; then
  mkdir -p "/var/lock/git_repo_check"
fi

# Check if the lock file exists and exit if it does
if [ -f "$lock_file" ]; then
  echo "Error: Lock file already exists. Exiting."
  exit 1
fi

# Create the lock file
touch $lock_file

# Function to check if a directory is a Git repository
is_git_repo() {
  dir=$1
  if [ -d "$1/.git" ]; then
    return 0
  else
    return 1
  fi
}

# Function to check for Git repository changes
check_git_repo() {
  dir=$1
  (
    cd "$dir"

    if git pull | grep -q "^CONFLICT"; then
        echo "Error: Pull conflicts detected. Aborting."
    fi

    status=$(git status --porcelain)
    if [ ! -z "$status" ]; then
      echo -e $dir "\t Repository has changes that haven't been committed."
    fi

    # Check if the local repository is behind the remote repository
    remote=$(git ls-remote --heads origin | grep "refs/heads/main\|refs/heads/master" | cut -f1)
    local=$(git rev-parse HEAD)
    if  [ "$local" != "$remote" ] || [ ] ; then
      echo -e $dir " \t Local repository is behind the remote repository."
    fi
  )
}

# Array to store PIDs of background processes
pids=()

# Search for Git repositories
for dir in $(find . -maxdepth $max_depth -type d); do
  if is_git_repo "$dir"; then
    check_git_repo "$dir" &
    pids+=($!)
  fi
done

# Wait for all background processes to complete
for pid in ${pids[*]}; do
  wait $pid
done

# Remove the lock file
rm "$lock_file"
  
