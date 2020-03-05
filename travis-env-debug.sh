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
