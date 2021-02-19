# Version history

We follow [Semantic Versions](https://semver.org/).


## Version 0.2.2 (unreleased)

- Update dependencies and setup.cfg
- Add navigation links to the previous and the next post
- Increase delays before updating posts
- Ignore post update errors (to proceed with other tasks)


## Version 0.2.1

- Update dependencies and setup.cfg


## Version 0.2.0

- Update the link to the Status image in the README file
- Update dependencies
- Extend the `Config` to allow storing more items locally (using YAML)
- Initialize the `Config` inside the `App` class to handle errors during the `Config` loading
- Add `Schedule`, `ScheduleStorage` and `ScheduleFileStorage` classes for storing scheduled posts
- Change the post scheduling to the UTC time
- Implement the post scheduling based on the data provided by the `Schedule` class
- Add the `ScheduleWikiStorage` class for storing scheduled posts on Reddit's wiki


## Version 0.1.8

- Update dependencies
- Replace `dotty-dict` with `scalpl` to avoid compatibility issues on Windows 10 with Japanese locale
- Use a random port number for testing the HTTP server (to ensure the port is available)


## Version 0.1.7

- Add `ruamel.yaml` to dependencies (missing when installed on Windows)


## Version 0.1.6

- Refactor the `Scheduler` to improve the exception handling when loading the scheduled post
- Move the `EmptySchedule` checking from the `Timer` to the `Scheduler`
- Add the `RedditHelper` class - providing the Reddit's API methods unsupported by `PRAW`
- Add the `PostImage` class - representing an image in a Reddit post
- Add the `TextPostConverter` class - converting from Markdown to Reddit Rich Text JSON
- Update the `Post` to include the attributes needed for submitting a post with thumbnail
- Implement loading of posts with thumbnails to the `Scheduler`
- Implement post submission with thumbnails to the `RedditCutifier`
- Implement post updating to the `RedditCutifier` for restoring the original Markdown of the posts with thumbnail


## Version 0.1.5

- Implement the post submission to the `RedditCutifier`
- Add the post submission via the `RedditCutifier` to the `App`
- Add the `ConfigStorage` class - storing the refresh token
- Implement the storing of the refresh token to the `Config`
- Add the authorization with the refresh token to the `OAuthHelper`


## Version 0.1.4

- Add `Jinja` templates with cute GIFs - used for the OAuth callback
- Add `flask` to dependencies
- Add the `http_server` module - handling the OAuth callback
- Add `praw` to dependencies
- Add the `OAuthHelper` class - providing the methods for the Reddit authorization
- Add the `RedditCutifier` class - making Reddit a cuter place
- Add Reddit authorization via the `RedditCutifier` to the `App`


## Version 0.1.3

- Add class `Timer` - responsible for waiting until the scheduled time
- Add the `Timer` to the `App`
- Add rendering of the remaining time during the countdown


## Version 0.1.2

- Add class `Post` - representing the Reddit post
- Add class `Scheduler` - managing data about scheduled posts
- Add a creation of a sample scheduled post
- Add the `Scheduler` to the `App`


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
