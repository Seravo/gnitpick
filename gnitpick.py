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
    email_domains = None
    verbose = None

    def __init__(self, git_rev, *, email_domains=None, verbose=None):
        """Create a list of hashes to be inspected."""
        # NOTE! Don't use --ancestry-path as origin/master is likely no longer
        # a direct ancestry as this new commit branched off before master HEAD.
        cmd = ['git', 'rev-list', '--max-count=100', git_rev]
        commits = self._git_shell_command(cmd)
        # Use list comprehension to strip out empty lines
        commits = [i for i in commits if i]

        if email_domains:
            self.email_domains = email_domains

        if verbose:
            self.verbose = verbose

        if len(commits) < 1:
            print("No commits in range {}".format(git_rev))
            print("Using origin/master..HEAD instead.")
            cmd = ['git', 'rev-list', '--max-count=100', 'origin/master..HEAD']
            commits = self._git_shell_command(cmd)

        # In the special case that we detect a Travis-CI job running on a
        # simulated PR branch to master branch merge, then skip the first
        # commit as it is artificial and made by Travis-CI itself
        if os.getenv('TRAVIS_PULL_REQUEST_BRANCH') and \
                os.getenv('TRAVIS_BRANCH') == 'master' and \
                os.getenv('TRAVIS_PULL_REQUEST_BRANCH') != \
                os.getenv('TRAVIS_BRANCH'):
            commits = commits[1:]

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
            self.inspect_author_name()
            self.inspect_author_email()
            self.inspect_commit_message()
            # Add other steps here
            self.current_commit += 1

        if len(self.fails) > 0:
            print("Gnitpick commit inspection did not pass!")
            print()  # New line for clarity
            print("Fix these fails and try again:")
            self.print_fails()
            print()
            print("Read more about about git best practices at")
            print("https://github.com/Seravo/gnitpick#recommended-reads")
            exit(1)
        else:
            print("Gnitpick commit inspection passed!")

    def print_fails(self):
        """Print fails."""
        for item in self.fails:
            print('- {}: {}'.format(item['commit'], item['message']))

    def inspect_author_name(self):
        """Inspect author name."""
        # Only consider the first author email from result set
        author_name = self._get_commit_info('aN')[0]

        if self.verbose:
            print(f'--> Checking author name "{author_name}"')

        if not author_name[0].isupper():
            self.fails.append({
                'commit': self.commit_hashes[self.current_commit],
                'message': "Author name '{}' does not start with "
                           "an uppercase letter".format(author_name)
            })

    def inspect_author_email(self):
        """Inspect author email address."""
        # Only consider the first author email from result set
        email = self._get_commit_info('aE')[0]
        author_email_domain = email.split("@")[1]

        if self.verbose:
            print(f'--> Checking author email "{author_email_domain}"')

        if self.email_domains and \
           author_email_domain not in self.email_domains:
            self.fails.append({
                'commit': self.commit_hashes[self.current_commit],
                'message': "Commit author email '{}' is does not match any of "
                           "the required email domains: {}"
                           .format(email, ", ".join(self.email_domains))
            })

    def inspect_commit_message(self):
        """Inspect commit message contents."""
        message = self._get_commit_info('B')

        # First line of message is the title
        title = message[0]

        if self.verbose:
            print(f'--> Checking commit title "{title}"')

        # The title should not end in a period, ever
        if title[len(title)-1] == '.':
            self.fails.append({
                'commit': self.commit_hashes[self.current_commit],
                'message': "Commit message title '{}' ends in a period"
                           " character".format(title)
            })

        special_commit = False
        if title.startswith('Merge') or \
           message[0].startswith('This reverts commit'):
            special_commit = True

        # The title should be max 72 characters long if it is a normal commit
        # (and not e.g. a revert commit)
        if len(title) > 72 and not special_commit:
            self.fails.append({
                'commit': self.commit_hashes[self.current_commit],
                'message': "Commit message title '{}' is over 72 characters"
                           .format(title)
            })

        # If the first word references an issue or file check if differently
        # eg. "xyz-123: The title", "one.py, two.py: The title",
        #     "[123]: The title" or "MDEV-1234: The title"
        # When modifying this, verify with https://www.regexpal.com/
        if re.match(r'^([a-zA-Z0-9-.\[\]])+(, [a-zA-Z0-9-.\[\]]+)?:', title):
            pass
        else:
            # The title should start with an uppercase letter
            if not title[0].isupper():
                self.fails.append({
                    'commit': self.commit_hashes[self.current_commit],
                    'message': "Commit message title '{}' does not start with "
                               "an uppercase letter".format(title)
                })

        # Merge requests should not include merges themselves
        if title[0:14] == "Merge branch '":
            self.fails.append({
                'commit': self.commit_hashes[self.current_commit],
                'message': "Merge request includes merges by itself"
            })


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        'git_revision_range', metavar='revision', nargs='?',
        help='Git revision range to test (defaults to remote master commit, '
             'origin/master..HEAD)')
    parser.add_argument(
        '--target-branch',
        help='Target branch remote and name (defaults to "master")')
    parser.add_argument(
        '--target-repository',
        help='Target repository name or address if should compare across '
             'repos (defaults to "origin")')
    parser.add_argument(
        '--email-domains',
        help='Comma separated list of allowed author email domains, '
             ' e.g seravo.com,seravo.fi')
    parser.add_argument(
        '--verbose', default=False, action='store_true',
        help='Enable in verbose mode')

    # First check that git is installed and this is running in a git repository
    try:
        cmd = ['git', 'status']
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL)
    except FileNotFoundError:
        print("Command 'git' not found, aborting Gnitpick")
        exit(2)
    except subprocess.CalledProcessError as e:
        if e.returncode == 128:
            print("Gnitpick failed to run in directory: {}".
                  format(subprocess.check_output(
                    ['pwd'], universal_newlines=True)))
            exit(e.returncode)

        else:
            raise RuntimeError("Running {} failed!".format(" ".join(cmd)))

    args = parser.parse_args()

    if not args.target_branch:
        # Default value
        target_branch = 'master'

    if not args.target_repository:
        # Default value
        target_repository = 'origin'
    else:
        print(f'Checking against target repository "{args.target_repository}"')

        # Check if remote starts with https:// or ends with .git
        if args.target_repository[0:8] == 'https://' or \
           args.target_repository[-4:] == '.git':
            # Add new remote with name 'gnitpick-reference' and use it
            target_repository = 'gnitpick-reference'
            subprocess.check_call([
                'git', 'remote', 'add',
                target_repository, args.target_repository])

        else:
            target_repository = args.target_repository

        # Check if repository with that name is already configured
        remotes = subprocess.check_output(['git', 'remote'])
        if target_repository not in str(remotes):
            raise RuntimeError(
                f'Given remote name {target_repository} '
                'does not exists, aborting Gnitpick')

        # Start tracking remote branch
        subprocess.check_call([
            'git', 'remote', 'set-branches', '--add',
            target_repository, target_branch])
        # Fetch remote branch that is tracked
        subprocess.check_call([
            'git', 'fetch', target_repository, target_branch])

    if args.git_revision_range:
        # Use command-line argument if given
        git_rev = args.git_revision_range

        # Make revision a range if it wasn't already
        if '..' not in git_rev:
            git_rev += '..HEAD'

        if args.target_branch:
            print(f'Ignoring branch "{args.target_branch}" as exact revision '
                  f'range {args.git_revision_range} has been given')

    elif os.getenv('TRAVIS') and \
            not args.target_branch and not args.target_repository:
        # Use Travis environment variables only if no override exists
        print("Travis-CI detected, reading git revisions from environment")

        # See https://docs.travis-ci.com/user/environment-variables/#default \
        # -environment-variables.
        travis_range = os.getenv('TRAVIS_COMMIT_RANGE')

        # When a branch is force-pushed, Travis CI will return some old
        # commit hashes that no longer exist after force-pushing: see
        # https://github.com/travis-ci/travis-ci/issues/2668.
        # Therefore we need to test the range is valid.
        # NOTE! Don't use --ancestry-path as origin/master is likely no longer
        # a direct ancestry as this new commit branched off before master HEAD.
        try:
            cmd = ['git', 'rev-list', '--max-count=100', travis_range]
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(e.returncode)
            if e.returncode == 128:
                print("Cannot compare {}, is this a force push?".
                      format(travis_range))
                # Fall back to testing comparing against target branch
                git_rev = f'{target_repository}/{target_branch}..HEAD'
            else:
                raise RuntimeError("Git command failed!")
        else:
            # OK to use TRAVIS_COMMIT_RANGE
            git_rev = travis_range

    else:
        # If no git revision range was given, and Travis-CI not detected, then
        # default to compare HEAD to the target branch where we assume it
        # branched off from
        git_rev = f'{target_repository}/{target_branch}..HEAD'

    # One more time ensure we can see the range we can compare
    # NOTE! Don't use --ancestry-path as origin/master is likely no longer
    # a direct ancestry as this new commit branched off before master HEAD.
    try:
        cmd = ['git', 'rev-list', '--max-count=100', git_rev]
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        if e.returncode == 128:
            print("Cannot compare {}, attempting to fetch more commits".
                  format(git_rev))
            # Start tracking remote branch
            subprocess.check_call([
                'git', 'remote', 'set-branches', '--add',
                target_repository, target_branch])
            # Fetch remote branch that is tracked
            subprocess.check_call([
                'git', 'fetch', target_repository, target_branch])
        else:
            raise RuntimeError('Git command failed!')

    print("Gnitpick inspecting git revisions range {}".format(git_rev))

    if args.email_domains:
        email_domains = args.email_domains.split(",")
    else:
        email_domains = None

    Gnitpick(
        git_rev,
        email_domains=email_domains,
        verbose=args.verbose
    ).run()
