import os
from os.path import dirname, realpath, join

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from server.lib.response import json_success
from server.lib.db import fetch_content_using_ids


def home(request: HttpRequest) -> HttpResponse:
  return render(request, "home.html", {})

@csrf_exempt
def upload(request: HttpRequest) -> HttpResponse:
  rule_file = list(request.FILES.values())[0]

  ROOT_DIR: str = dirname(dirname(realpath(__file__)))
  completeName = join(ROOT_DIR, "../rules.json")
  with open(completeName, "w") as f:
    f.write(rule_file.read().decode("UTF-8"))

  os.system("python manage.py execute_rules")

  msg_ids = open(join(ROOT_DIR, "../msg_ids.txt"), "r").read()
  msg_ids = msg_ids.split(',')

  return json_success(
    {"data": list(fetch_content_using_ids(msg_ids))}
  )

@csrf_exempt
def reset(request: HttpRequest) -> HttpResponse:
  os.system("python manage.py flush_db")
  return json_success()

@csrf_exempt
def signin(request: HttpRequest) -> HttpResponse:
  os.system("python manage.py google_oauth2")
  return json_success()

def elasticSearch(request: HttpRequest) -> HttpResponse:
  import requests
  searchWord = "scroll"
  url = "ngrok.io/abc" + f"?search={searchWord}&data={subjectData}"
  headers = { 'User-Agent': 'Mozilla/5.0' }
  return requests.get(
      url,
      headers=headers,
      stream=True
  )
  return render(request, "home.html", {})
