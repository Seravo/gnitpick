#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Travis CI test for Git commit standards.

A test script for validating in Travis CI that the Git commit is up-to-par
with our Git standards.
"""

import argparse
import os
import subprocess

DESCRIPTION = "Git commit message quality controller"


class Gnitpick():
    """Main function of script."""

    commit_hashes = []
    fails = []
    current_commit = 0
    email_domains = None

    def __init__(self, git_rev, *, email_domains=None):
        """Create a list of hashes to be inspected."""
        cmd = ['git', 'rev-list', '--max-count=100',
               '--ancestry-path', git_rev]
        commits = self._git_shell_command(cmd)
        # Use list comprehension to strip out empty lines
        commits = [i for i in commits if i]

        if email_domains:
            self.email_domains = email_domains

        if len(commits) < 1:
            print("No commits in range {}".format(git_rev))
            print("Using HEAD~10..HEAD instead.")
            cmd = ['git', 'rev-list', '--max-count=100',
                   '--ancestry-path', 'HEAD~10..HEAD']
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
        author_email_domain = email.split("@")[1]

        if self.email_domains and \
           author_email_domain not in self.email_domains:
            self.fails.append({
                'commit': self.commit_hashes[self.current_commit],
                'message': "Commit email '{}' is does not match any of "
                           "the required email domains: {}"
                           .format(email, ", ".join(self.email_domains))
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
    parser.add_argument(
        '--email-domains', nargs=1,
        help='Comma separated list of allowed author email domains, '
             ' e.g seravo.com,seravo.fi')
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
        travis_range = os.getenv('TRAVIS_COMMIT_RANGE')

        # When a branch is force-pushed, Travis CI will return some old
        # commit hashes that no longer exist after force-pushing: see
        # https://github.com/travis-ci/travis-ci/issues/2668.
        # Therefore we need to test the range is valid.
        try:
            cmd = ['git', 'rev-list', '--max-count=100',
                   '--ancestry-path', travis_range]
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as e:
            print(e.returncode)
            if e.returncode == 128:
                print("Cannot compare {}, is this a force push?".
                      format(travis_range))
                # Fall back to testing 10 latest
                git_rev = "HEAD~10..HEAD"
            else:
                raise RuntimeError("Git command failed!")
        else:
            # OK to use TRAVIS_COMMIT_RANGE
            git_rev = travis_range

    else:
        # Default: inspect just the latest commit
        git_rev = "HEAD~1..HEAD"

    print("Gnitpick inspecting git revisions range {}".format(git_rev))

    if args.email_domains:
        email_domains = args.email_domains[0].split(",")
    else:
        email_domains = None

    Gnitpick(
        git_rev,
        email_domains=email_domains
    ).run()
