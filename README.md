<p align="center">
  <img src="https://raw.githubusercontent.com/slow-start-fans/slow-start-rewatch/master/assets/happy_shion.gif" width="384" height="360" />
</p>


# Slow Start Rewatch

[![Build Status](https://travis-ci.com/slow-start-fans/slow-start-rewatch.svg?branch=master)](https://travis-ci.com/slow-start-fans/slow-start-rewatch)
[![Coverage](https://coveralls.io/repos/github/slow-start-fans/slow-start-rewatch/badge.svg?branch=master)](https://coveralls.io/github/slow-start-fans/slow-start-rewatch?branch=master)
[![Python Version](https://img.shields.io/pypi/pyversions/slow-start-rewatch.svg)](https://pypi.org/project/slow-start-rewatch/)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)


## Missions

Make cute things happen!

Provide a command-line utility for hosting an awesome Slow Start Rewatch.


## Features

- Schedule a submission of multiple Reddit posts
- The templates for posts can be stored in Reddit's wiki or local files
- Each post can include a navigation section with links to other posts which are automatically updated after the submission of new posts
- Reddit authorization via OAuth2 using a local HTTP server with cute GIFs
- Storing the refresh token locally to keep the authorization active
- Submitting text posts with thumbnails
- Fully typed with annotations and checked with mypy, [PEP561 compatible](https://www.python.org/dev/peps/pep-0561/)


## Installation

```bash
pip install slow-start-rewatch
```

Upgrade:

```bash
pip install -U slow-start-rewatch
```


## Usage

When started for the first time the location of the schedule must be set.

1. Using the schedule stored in Reddit's wiki:

```bash
slow-start-rewatch -w /r/subreddit/wiki/wiki-path
```

2. Using the schedule stored in the local YAML file:

```bash
slow-start-rewatch -f /path/to/the/schedule.yml
```

After the location of the schedule is stored in the local config, the program can be launched without any parameters:

```bash
slow-start-rewatch
```


## License

[MIT](https://github.com/slow-start-fans/slow-start-rewatch/blob/master/LICENSE)


## Credits

This project was generated with [`wemake-python-package`](https://github.com/wemake-services/wemake-python-package).

GitHub avatar art by [yunyunmaru](https://www.pixiv.net/en/users/24452545).
