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
cd mail-search
pip install -r requirements.txt

# Start the Django server
python manage.py runserver
# Use the UI to interact or you could just run the following scripts:

# In a separate terminal
python -m scripts.google_oauth2
python -m scripts.execute_rules
python -m scripts.flush_db
```
___

## UI Screen

![pic](https://user-images.githubusercontent.com/40122794/125173169-8d524a80-e1db-11eb-86f6-9c08a6515d33.png)

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
      view | mark_read | mark_unread: True
    },
    {
      move: Any value in `POSSIBLE_LABELS` (found in `models.py`)
    }
    ...
  ]
}

Note: Rules always start in Upper case.
Validation has been added for the API endpoints,
The script will terminate as soon as an error is encountered.
The database will always remain consistent with the actual values in GMail.
```
</details>

___

Requirements: Python 3.6+

Tesed on windows and linux

____