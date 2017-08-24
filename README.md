## Piazza Slack Bot

This bot will listen for any mention of it's name (e.g. `@piazza`) followed by a
post number, `@#`, or any Piazza post link and reply with a formatted version of
the post. Converting Piazza posts to Slack messages is a bit hacky (I use
html2text to convert Piazza's HTML to Markdown and then I manually convert the
Markdown to Slack's format), but it should work most of the time. The first
image found in the post will also be embedded directly in the Slack message.

Set the configuration values either through environment variables or manually
in `bot_config.py`. You'll want a Piazza account dedicated to the bot (the
API is unofficial, so you have to provide your password in the config). The bot
has to be a member of a Piazza to embed posts and it must be an instructor to
show anonymous student names and private posts. You can add the bot account to
any number of Piazzas, but `@#` and `@piazza #` only work for the course id set
in the config.

This app should be ready to deploy on Heroku or Dokku; just set the environment
variables, push, and you should be good to go.
