# Mail Search

### Setup and Usage:

* Follow the steps mentioned in the [`Google OAuth2 docs`](https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred).
  
  Or you could just click the `Enable` button at the [`Gmail API library of your GCP console`](https://console.cloud.google.com/apis/library/gmail.googleapis.com).
  Then set the Authorised redirect URIs to `http://localhost:8000/accounts/google/` for your OAuth 2.0 Client.

* Download the `client_secret.json` file from the API  Console and rename it to `credentials.json`

  **Note:** If you want to use a different redirect URI or client secret file, just update the appropriate values in the `config.ini` and `urls.py` file.

* `git clone git@github.com:ryanreh99/mail-search.git`

* [Activate the virtual environment](https://docs.python.org/3/tutorial/venv.html).

```shell
cd mail-server
python manage.py runserver
python google_oauth2.py # In a separate terminal
```