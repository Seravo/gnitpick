#!/bin/bash
# See https://docs.travis-ci.com/user/environment-variables/#default-environment-variables

echo "Debug TRAVIS_CI environment variables:"

for x in \
  TRAVIS_BRANCH TRAVIS_COMMIT TRAVIS_COMMIT_RANGE \
  TRAVIS_PULL_REQUEST_BRANCH TRAVIS_PULL_REQUEST_SHA \
	TRAVIS_PULL_REQUEST_SLUG TRAVIS_REPO_SLUG
do
	echo "$x:" ${!x}
done

echo "Debug available refs on current branch:"

set -x # Print out commands
git remote -v
git branch -a
git log --oneline HEAD~10
git show-branch
git show-branch --merge-base
git merge-base --fork-point master HEAD
git symbolic-ref HEAD
set +x

for x in HEAD~{0..10}
  do echo grep -rF "$(git rev-parse $x)" .git/refs/*
  grep -rF "$(git rev-parse $x)" .git/refs/*
done

# Make rest of document silent, for source documentation only
exit 0
echo > /dev/null << EOF
###

Example of a normal push on the master branch:

	TRAVIS_BRANCH: master
	TRAVIS_COMMIT: d4a1fbc940742eb544a4c262efc6f184d2889e3e
	TRAVIS_COMMIT_RANGE: c6aad588e924...d4a1fbc94074
	TRAVIS_PULL_REQUEST_BRANCH:
	TRAVIS_PULL_REQUEST_SHA:
	TRAVIS_PULL_REQUEST_SLUG:
	TRAVIS_REPO_SLUG: Seravo/gnitpick

Example of force push on the commit above:

	TRAVIS_BRANCH: master
	TRAVIS_COMMIT: eba29444d494b19af4f002b3a4327d12eb6bf86f
	TRAVIS_COMMIT_RANGE: d4a1fbc94074...eba29444d494
	TRAVIS_PULL_REQUEST_BRANCH:
	TRAVIS_PULL_REQUEST_SHA:
	TRAVIS_PULL_REQUEST_SLUG:
	TRAVIS_REPO_SLUG: Seravo/gnitpick

Fails with:
	Gnitpick inspecting git revisions range d4a1fbc94074...eba29444d494
	fatal: ambiguous argument 'd4a1fbc94074...eba29444d494': unknown revision or
	path not in the working tree.

Commit d4a1fbc94074 refers to the old commit before it was amended, while
eba29444d494 is the new commit that replaced the old one.

Example of a push of a new branch:

	TRAVIS_BRANCH: test-pr
	TRAVIS_COMMIT: 66c96d0b399087f60ce66107caf6a8db117642be
	TRAVIS_COMMIT_RANGE: 1c7e87c17181^...66c96d0b3990
	TRAVIS_PULL_REQUEST_BRANCH:
	TRAVIS_PULL_REQUEST_SHA:
	TRAVIS_PULL_REQUEST_SLUG:
	TRAVIS_REPO_SLUG: Seravo/gnitpick

Example of a push on an existing branch:

	TRAVIS_BRANCH: test-pr
	TRAVIS_COMMIT: 90e7a7b1c94c8481f3f13bbbdceb7728fbd9ae2c
	TRAVIS_COMMIT_RANGE: 66c96d0b3990...90e7a7b1c94c
	TRAVIS_PULL_REQUEST_BRANCH:
	TRAVIS_PULL_REQUEST_SHA:
	TRAVIS_PULL_REQUEST_SLUG:
	TRAVIS_REPO_SLUG: Seravo/gnitpick

Example of a new pull request inside the same repository:

	TRAVIS_BRANCH: master
	TRAVIS_COMMIT: cd6793d3496c6d5bd5846819bcd1edf2d7df3d73
	TRAVIS_COMMIT_RANGE: a10529ef030f1628e0fc4f981b63b530e6f3a6db...90e7a7b1c94c8481f3f13bbbdceb7728fbd9ae2c
	TRAVIS_PULL_REQUEST_BRANCH: test-pr
	TRAVIS_PULL_REQUEST_SHA: 90e7a7b1c94c8481f3f13bbbdceb7728fbd9ae2c
	TRAVIS_PULL_REQUEST_SLUG: Seravo/gnitpick
	TRAVIS_REPO_SLUG: Seravo/gnitpick

The TRAVIS_COMMIT reflects the merge commit, if one was to be made. The
TRAVIS_COMMIT_RANGE represents the actual range of commits in the PR.

Example of git refs debug results:

+git remote -v
origin	https://github.com/Seravo/gnitpick.git (fetch)
origin	https://github.com/Seravo/gnitpick.git (push)

+git branch -a
* (HEAD detached at ef691e9)
  dev-otto
  remotes/origin/dev-otto

+git log --oneline HEAD~10
6c2790a Use TRAVIS_COMMIT_RANGE and do not assume anything about master branch
a10529e Document TRAVIS_COMMIT_RANGE in force push situations
eba2944 Start inspecting the commits in this repo iself in Travis-CI
c6aad58 Fix code style: E251 unexpected spaces around keyword / parameter equals
d3e9a51 Create a git pre-push hook example that also applies to this repo itself
13ad6d9 Misc tweaks for prettier output
18d502a Refactor script with argparse to support being run locally (Closes: #1)
944fed9 Enforce PEP-8 with automatic Flake8 testing via Travis-CI
6637604 Update README to reflect that the project is in an early stage
c04f9ec Make Python code PEP-8 compatible
c9013d5 Add README and license
e41bbc5 Add test for Git best-practices

grep -rF ef691e95f926507a2b49815a6f9cc2cc229db5c2 .git/refs/heads .git/refs/tags
grep -rF ef73043e9e44dfaf7cb368fe16ab16ef4f56b1c0 .git/refs/heads .git/refs/tags
grep -rF 80d02de240c0c530fc24bf379e6af5b5a40570f0 .git/refs/heads .git/refs/tags
grep -rF a3ae91523bca6cc0d32f935cb7c748a47609af9c .git/refs/heads .git/refs/tags
grep -rF 7f109064c42c7c29d02deab56f6a80095b9d13bd .git/refs/heads .git/refs/tags
grep -rF 15e40eb0af7e23687c4d76cba5277d47898338ec .git/refs/heads .git/refs/tags
grep -rF 323f4803aa409b947012cdf91ea9737bccfe8c9f .git/refs/heads .git/refs/tags
grep -rF b7e8bab9c61ed75810573436e9220aadbf80ec2f .git/refs/heads .git/refs/tags
grep -rF 57229fcb122611f870f6ffd7d189d203ae02416b .git/refs/heads .git/refs/tags
grep -rF e4646fad61fd67e1b23c42f5608232d59087d09c .git/refs/heads .git/refs/tags
grep -rF 6c2790a42fa624f1079cbf94235807902e446b42 .git/refs/heads .git/refs/tags

EOF
