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
