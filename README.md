# Test Cloud Foundry FTP
This service demonstrates the succesful use of ftp protocols by apps deployed to Cloud Foundry.

## Pre-Requisites
- A running CloudFoundry instance
- Cloud Foundry CLI tools

## How to deploy

```bash
$ cf login -a <api_url> -u <sdx_user> <password> <sdx_user_password>


$ cf push sdx-cf-go-deploy
```

You can find what url the app is running at with:

```bash
$ cf apps
```

## Testing
The app has one endpoint:
- `<url>/files (GET)` - returns a list of JSON file names located on the FTP server

## Running with Concourse
- Requires a running concourse instance
- Pipeline code is found under `/ci`
- As this is (currently) a private repo it requires a private key fle to access. This needs to be added as an environment variable in a credentials.yml file added to the `fly`:

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
  -----END RSA PRIVATE KEY----
```

```bash
$ fly -t <concourse_name> set-pipeline --config pipeline.yml --pipeline sdx-spike --load-vars-from credentials.yml
```

### License

Copyright © 2017 Crown Copyright (Office for National Statistics) (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE) for details.
