# Gnitpick

Git commit message [nitpicker](https://en.wiktionary.org/wiki/nitpick). Makes sure all future git commit messages are perfect!

## Usage

In you git pre-commit hook or CI system, simply run:

    python3 /path/to/gnitpick.py

### Local git hook

See `git-hooks/pre-push` as an example.

### Travis-CI

Simply add this to your `.travis.yml` file:

    - curl -O https://raw.githubusercontent.com/Seravo/gnitpick/master/gnitpick.py
    - python3 ./gnitpick.py

## Development status

Early stages... Pull requests welcome!

## License

This script is published under GPLv3. Feel free to use. Contributions welcome!
