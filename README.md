# Mail Search

## Setup and Usage:

* Follow the steps mentioned in the [`Google OAuth2 docs`](https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred).
  
  Or you could just click the `Enable` button at the [`Gmail API library of your GCP console`](https://console.cloud.google.com/apis/library/gmail.googleapis.com).
  Then set the Authorised redirect URIs to `http://localhost:8000/accounts/google/` for your OAuth 2.0 Client.

* Download the `client_secret.json` file from the API  Console and rename it to `credentials.json`

  **Note:** If you want to use a different redirect URI or client secret file, just update the appropriate values in the `config.ini` and `urls.py` file.

* Place the `client_secret.json` and `rules.json` files in the `mail-search` directory.

```shell
git clone git@github.com:ryanreh99/mail-search.git
# Activate the virtual environment
cd mail-server
pip install -r requirements.txt

# Start the Django server
python manage.py runserver
python -m scripts.google_oauth2 # In a separate terminal

# Run the script to execute your actions
python -m scripts.execute_rules


# To test another user: reset the db by running
python -m scripts.flush_db
```
___

## API Documentation:

View the `mail_search.yaml` file.

OR

Go to [`swaggerhub/ryanreh99/mail-search`](https://app.swaggerhub.com/apis/ryanreh99/mail-search/1.0.0).

___

## Rules File Documentation

<details>
<summary>Click Here</summary>
<br>

```
Check the sample rules.json file.
These are the other values in can take:

{
  type: All | Any
  rules: [
    ...
    {
      field: From | To | Subject
      predicate: Contains | Not equals
      value: Any value.
    }
    {
      field: Date Received
      predicate: Less than | Greater than
      value: A valid date in "DD/MM/YYYY" format.
    }
    ...
  ]
  actions: [
    ...
    {
      view: True
    },
    {
      mark_read | mark_unread: True
    },
    {
      move: Any value in `POSSIBLE_LABELS` (found in `models.py`)
    }
    ...
  ]
}

Note: Rules always start in Upper case.
Validation has been added for the API endpoints,
not for the `execute_rules.py` script.
```
</details>