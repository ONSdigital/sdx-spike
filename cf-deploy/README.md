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

Testing
-------

The app exposes 2 endpoints:

  - ``<url>/pony (GET)`` - lists the MLP Mane 6
  - ``<url>/pony/<ponyname> (GET)`` - returns the information for that pony


Running with Concourse
----------------------

  - Requires a running concourse instance
  - Pipeline code is found under `/ci`
  - As this is (currently) a private repo it requires a private key file to
    access. This needs to be added as an environment var in a `credentials.yml`
    file added to the `fly`:

```yaml
cf_api_url: https://example.com
cf_username: username
cf_password: password
cf_organisation: my-org
cf_space: my-space

github_private_key: |
  -----BEGIN RSA PRIVATE KEY-----
  MIIJKgIBAAKCAaoc4qhjxhdjaks14sT/NC4C90DRZzJHbk/HiN4S0ohxXiPD5Xis
  ...
  <snipped lots of lines>
  ...
  Qi5wmqQdfajcceZ8o6P/WQGc9gm+FsTwszGMSJXndjabcQi7qesob5yMvNX9lg==
  -----END RSA PRIVATE KEY-----
```

```shell
$ fly -t <concourse_name> set-pipeline --config pipeline.yml --pipeline sdx-pony --load-vars-from credentials.yml
```