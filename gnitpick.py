#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

"""Travis CI test for Git commit standards.

A test script for validating in Travis CI that the Git commit is up-to-par
with our Git standards.
"""

import os
import re
import subprocess


class GitCommitTest():
    commit_hashes = []
    test_failures = []
    current_commit = 0

    def __init__(self):
        self._setup_commit_range()

    def run(self):
        print("Starting Git commit tests for commits {}..."
              .format(', '.join(self.commit_hashes)))
        for self.current_commit in range(len(self.commit_hashes)):
            print(
                "Testing commit {}...".format(
                    self.commit_hashes[self.current_commit]
                )
            )
            self.test_commit_email()
            self.test_commit_message()
            # Add other steps here
            self.current_commit += 1

        if len(self.test_failures) > 0:
            print("Git commit tests failed!")
            print("Failed examples:")
            self.print_failures()
            exit(1)

    def print_failures(self):
        for item in self.test_failures:
            print('{}: {}'.format(item['commit'], item['message']))

    def test_commit_email(self):
        email = self._get_commit_info('aE')
        if not re.match(r'.*@seravo\..+$', email):
            self.test_failures.append({
                'commit': self.commit_hashes[self.current_commit],
                'message': "Commit email '{}' is not provided by Seravo"
                           .format(email)
            })

    def test_commit_message(self):
        message = self._get_commit_info('B')
        message_parts = message.split('\n\n', 1)
        title = message_parts[0]

        # The title should be max 72 characters long if it is a normal commit
        # (and not e.g. a revert commit)
        if len(title) > 72 and "This reverts commit" not in message:
            self.test_failures.append({
                'commit': self.commit_hashes[self.current_commit],
                'message': "Commit message title '{}' is over 72 characters"
                           .format(title)
            })

        # The title should start with an uppercase letter
        if not title[0].isupper():
            self.test_failures.append({
                'commit': self.commit_hashes[self.current_commit],
                'message': "Commit message title '{}' does not start with an"
                           " uppercase letter".format(title)
            })

        # The title should not end in a period
        if title[len(title)-1] == '.':
            self.test_failures.append({
                'commit': self.commit_hashes[self.current_commit],
                'message': "Commit message title '{}' ends in a period"
                           " character".format(title)
            })
    def _setup_commit_range(self):
        # We need the master branch here
        self._fetch_master_branch()

        # See https://docs.travis-ci.com/user/environment-variables/#default \
        # -environment-variables.
        event_type = os.getenv('TRAVIS_EVENT_TYPE')
        travis_range = os.getenv('TRAVIS_COMMIT_RANGE')
        travis_branch = os.getenv('TRAVIS_BRANCH')

        # This script can only be run on Travis CI
        if event_type is None:
            raise RuntimeError("TRAVIS_EVENT_TYPE is not set – is this a"
                               " Travis CI job?")

        # If currently in a PR build, TRAVIS_BRANCH will contain the target
        # branch. However, in a Travis CI PR build the HEAD is in a detached
        # state with the commit in HEAD already containing a merge commit to
        # the master branch. That is why we should end the range to the
        # previous commit with HEAD~1 here.
        if event_type == 'pull_request':
            self.commit_hashes = self._get_rev_list(
                '{}..HEAD~1'.format(travis_branch)
            )
        else:
            # When a branch is force-pushed, Travis CI will return some old
            # commit hashes that no longer exist after force-pushing: see
            # https://github.com/travis-ci/travis-ci/issues/2668.
            # For that reason, we need to assume:
            # - Nobody force-pushes to master
            # - All branches originate from the master branch
            if travis_branch == 'master':
                # This will break when force pushing to master
                self.commit_hashes = self._get_rev_list(travis_range)
            else:
                self.commit_hashes = self._get_rev_list('master..HEAD')

    def _fetch_master_branch(self):
        cmd = ['git', 'fetch', 'origin', 'master:master']
        return subprocess.check_output(cmd).decode('utf-8').strip()

    def _get_commit_info(self, info):
        cmd = ['git', 'show', '-s', '--format=%{}'.format(info),
               self.commit_hashes[self.current_commit]]
        return subprocess.check_output(cmd).decode('utf-8').strip()

    def _get_rev_list(self, commit_range):
        cmd = ['git', 'rev-list', '--ancestry-path', commit_range]
        commits = subprocess.check_output(cmd).decode('utf-8').split('\n')
        return list(filter(None, commits))

if __name__ == '__main__':
    GitCommitTest().run()

