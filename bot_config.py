default_token = "SLACK-BOT-TOKEN"
default_piazza_id = "PIAZZA-COURSE-ID"
default_piazza_email = "PIAZZA-ACCOUNT-EMAIL"
default_piazza_password = "PIAZZA-ACCOUNT-PASSWORD"

import os

token = os.environ.get('PIAZZA_SLACK_BOT_TOKEN', default_token)
piazza_id = os.environ.get('PIAZZA_SLACK_BOT_COURSE', default_piazza_id)
piazza_email = os.environ.get('PIAZZA_SLACK_BOT_EMAIL', default_piazza_email)
piazza_password = os.environ.get('PIAZZA_SLACK_BOT_PASSWORD'), default_piazza_password)
