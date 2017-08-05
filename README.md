## Piazza Slack Bot

This bot will listen for any mention of it's name (e.g. `@piazza`) followed by a post number or any Piazza post link and reply with a formatted version of the post. Converting Piazza posts to Slack messages is a bit hacky (I use html2text to convert Piazza's HTML to Markdown and then I manually convert the Markdown to Slack's format), but it should work most of the time. The first image found in the post will also be embedded directly in the Slack message.

To configure, edit the following values in `bot_config.py`:

- `token` should be the bot's authorization token that you get from Slack
- `piazza_id` should be the course ID that you want to use when the bot is given a number (you can still give links to other courses)
- `piazza_email` should be the email for an account with access to all courses you want the bot to work with. If they are a student, the bot cannot display content for private posts or the names of anonymous students.
- `piazza_password` should be the password for the Piazza account (the API here is unofficial, so there's no auth tokens or anything like that)

Install the requirements in `requirements.txt` (probably in a virtualenv) and then run in Python 3. The bot does seem to crash occassionally when run continuously, so you may want to set it to run in a loop.
