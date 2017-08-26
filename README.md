## Piazza Slack Bot

This bot will embed Piazza posts in Slack. Any of the following post reference
formats can work:

- Any Piazza URL that the bot account is a member of (embeds main post)
- @&lt;bot username> &lt;post number>
- @&lt;post number>
- @&lt;post number>#&lt;followup number>

Set the configuration values either through environment variables or manually
in `bot_config.py`. You'll want a Piazza account dedicated to the bot (the
API is unofficial, so you have to provide your password in the config). The bot
has to be a member of a Piazza to embed posts and it must be an instructor to
show anonymous student names and private posts. You can add the bot account to
any number of Piazzas, but `@#` and `@piazza #` only work for the course id set
in the config.

This app should be ready to deploy on Heroku or Dokku; just set the environment
variables, push, and you should be good to go.
