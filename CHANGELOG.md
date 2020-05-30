# Version history

We follow [Semantic Versions](https://semver.org/).


## Version 0.1.2 (unreleased)

- Add class `Post` - representing the Reddit post


## Version 0.1.1

- Configure logging with `structlog`
- Implement `--debug` CLI option (sets the logging level to `DEBUG`)
- Add class `Config` that provides configuration for the Slow Start Rewatch
- Add a substitution of placeholders to the `Config` class
- Add class `App` - the main application class
- Add class `SlowStartRewatchException` - the base class for exceptions
- Set up exception handling
- Add `prepare` and `start` blocks to `App`


## Version 0.1.0

- Initial release
- Use double quotes for string literals
- Set up CLI with `click`
- Implement `--version` CLI option to show the current version
