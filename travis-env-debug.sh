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

exit 0

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
