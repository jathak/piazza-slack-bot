## Piazza Slack Bot

![Example](http://i.imgur.com/UGWJCqa.png)

This bot will listen for any mention of it's name (e.g. `@piazza`) followed by a post number or any Piazza post link and reply with a formatted version of the post.

To configure, edit the following values in `bot_config.py`:

- `token` should be the bot's authorization token that you get from Slack
- `piazza_id` should be the course ID that you want to use when the bot is given a number (you can still give links to other courses)
- `piazza_email` should be the email for an account with access to all courses you want the bot to work with. If they are a student, the bot will not display content for private posts.
- `piazza_password` should be the password for the Piazza account (the API here is unofficial, so there's no auth tokens or anything like that)

Install the requirements in `requirements.txt` (probably in a virtualenv) and then run in Python 3
