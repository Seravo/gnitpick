#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Travis CI test for Git commit standards.

A test script for validating in Travis CI that the Git commit is up-to-par
with our Git standards.
"""

import argparse
import os
import re
import subprocess

DESCRIPTION = "Git commit message quality controller"


class Gnitpick():
    """Main function of script."""

    commit_hashes = []
    fails = []
    current_commit = 0

    def __init__(self, git_rev):
        """Create a list of hashes to be inspected."""
        cmd = ['git', 'rev-list', '--max-count=100',
               '--ancestry-path', git_rev]
        commits = self._git_shell_command(cmd)
        self.commit_hashes = list(filter(None, commits))

    def _git_shell_command(self, cmd):
        # print("Command:")
        # print(" ", " ".join(cmd))
        result = subprocess.check_output(cmd).decode('utf-8').strip()
        result = result.split("\n")
        # print("Result:")
        # print(" ", "\n  ".join(result))
        # print("\n")
        return result

    def _get_commit_info(self, info):
        cmd = ['git', 'show', '-s', '--format=%{}'.format(info),
               self.commit_hashes[self.current_commit]]
        return self._git_shell_command(cmd)

    def run(self):
        """Start inspection."""
        git_log = self._git_shell_command(['git', 'log', git_rev])
        print("", "\n ".join(git_log))
        print()  # New line for clarity

        for self.current_commit in range(len(self.commit_hashes)):
            print(
                "Inspecting commit {}:".format(
                    self.commit_hashes[self.current_commit]
                )
            )
            self.inspect_commit_email()
            self.inspect_commit_message()
            # Add other steps here
            self.current_commit += 1

        if len(self.fails) > 0:
            print("Gnitpick commit inspection did not pass!")
            print()  # New line for clarity
            print("Fix these fails and try again:")
            self.print_fails()
            exit(1)
        else:
            print("Gnitpick commit inspection passed!")

    def print_fails(self):
        """Print fails."""
        for item in self.fails:
            print('- {}: {}'.format(item['commit'], item['message']))

    def inspect_commit_email(self):
        """Inspect committer email address."""
        # Only consider the first author email from result set
        email = self._get_commit_info('aE')[0]
        if not re.match(r'.*@seravo\..+$', email):
            self.fails.append({
                'commit': self.commit_hashes[self.current_commit],
                'message': "Commit email '{}' is not provided by Seravo"
                           .format(email)
            })

    def inspect_commit_message(self):
        """Inspect commit message contents."""
        message = self._get_commit_info('B')

        # First line of message is the title
        title = message[0]

        # The title should be max 72 characters long if it is a normal commit
        # (and not e.g. a revert commit)
        if len(title) > 72 and "This reverts commit" not in message:
            self.fails.append({
                'commit': self.commit_hashes[self.current_commit],
                'message': "Commit message title '{}' is over 72 characters"
                           .format(title)
            })

        # The title should start with an uppercase letter
        if not title[0].isupper():
            self.fails.append({
                'commit': self.commit_hashes[self.current_commit],
                'message': "Commit message title '{}' does not start with an"
                           " uppercase letter".format(title)
            })

        # The title should not end in a period
        if title[len(title)-1] == '.':
            self.fails.append({
                'commit': self.commit_hashes[self.current_commit],
                'message': "Commit message title '{}' ends in a period"
                           " character".format(title)
            })


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        'git_revision_range', metavar='revision', nargs='?',
        help='Git revision range to test (defaults to latest commit, '
             'HEAD~1..HEAD)')
    args = parser.parse_args()

    if args.git_revision_range:
        # Use command-line argument if given
        git_rev = args.git_revision_range

        # Make revision a range if it wasn't already
        if '..' not in git_rev:
            git_rev += '..HEAD'

    elif os.getenv('TRAVIS'):
        print("Travis-CI detected, reading git revisions from environment")

        # See https://docs.travis-ci.com/user/environment-variables/#default \
        # -environment-variables.
        travis_event_type = os.getenv('TRAVIS_EVENT_TYPE')
        travis_range = os.getenv('TRAVIS_COMMIT_RANGE')
        travis_branch = os.getenv('TRAVIS_BRANCH')

        # This script can only be run on Travis CI
        if travis_event_type is None:
            raise RuntimeError("TRAVIS_EVENT_TYPE is not set – is this a"
                               " Travis CI job?")

        # If currently in a PR build, TRAVIS_BRANCH will contain the target
        # branch. However, in a Travis CI PR build the HEAD is in a detached
        # state with the commit in HEAD already containing a merge commit to
        # the master branch. That is why we should end the range to the
        # previous commit with HEAD~1 here.
        if travis_event_type == 'pull_request':
            git_rev = '{}..HEAD~1'.format(travis_branch)
        else:
            # When a branch is force-pushed, Travis CI will return some old
            # commit hashes that no longer exist after force-pushing: see
            # https://github.com/travis-ci/travis-ci/issues/2668.
            #
            # This will break when force pushing to master
            git_rev = travis_range

    else:
        # Default: inspect just the latest commit
        git_rev = "HEAD~1..HEAD"

    print("Gnitpick inspecting git revisions range {}".format(git_rev))

    Gnitpick(git_rev).run()
