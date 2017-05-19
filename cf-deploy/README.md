Test Cloud Foundry Deploy
=========================

This service is for simple testing of deploying applications to Cloud Foundry

Pre-Requisites
--------------

  - A running Cloud Foundry instance
  - Cloud Foundry CLI tools

How to deploy
-------------

```shell
$ cf login -a <api_url> -u <sdx_user>
password> <the_sdx_user_password>

$ cf push sdx-cf-go-deploy
```

You can find what url the app is running at with:
```shell
$ cf apps
```