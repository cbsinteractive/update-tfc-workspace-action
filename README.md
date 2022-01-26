# Update TFC Workspace

A GitHub Action used to update Terraform Cloud workspace properties.

[![Lint and Test](https://github.com/cbsinteractive/update-tfc-workspace-action/actions/workflows/lint-and-test.yml/badge.svg)](https://github.com/cbsinteractive/update-tfc-workspace-action/actions/workflows/lint-and-test.yml)

## Inputs

The action expects the following inputs:

| Variable                | Required | Type    | Default | Description                                                                 |
| ----------------------- | -------- | ------- | ------- | --------------------------------------------------------------------------- |
| `tfcToken`              | Yes      | string  |         | A Terraform Cloud API token with access to manage the workspace             |
| `orgName`               | Yes      | string  |         | The name of the Terraform Cloud organization in which the workspace resides |
| `workspaceName`         | Yes      | string  |         | The name of the Terraform Cloud workspace to manage                         |
| `setDescription`        | No       | string  |         | The workspace description                                                   |
| `setWorkingDirectory`   | No       | string  |         | The directory that Terraform will execute within                            |
| `setVCSIdentifier`      | No       | string  |         | The VCS repo to connect, e.g. some-org/some-repo                            |
| `setVCSBranch`          | No       | string  |         | The VCS repo branch to connect                                              |
| `setVCSOAuthTokenID`    | No       | string  |         | The OAuth token ID used to authorize the connection                         |
| `unsetDescription`      | No       | boolean | false   | Unset the workspace description                                             |
| `unsetWorkingDirectory` | No       | boolean | false   | Unset the directory that Terraform will execute within                      |
| `unsetVCSIdentifier`    | No       | boolean | false   | Unset the VCS repo to connect, e.g. some-org/some-repo                      |
| `unsetVCSBranch`        | No       | boolean | false   | Unset the VCS repo branch to connect                                        |
| `unsetVCSOAuthTokenID`  | No       | boolean | false   | Unset the OAuth token ID used to authorize the connection                   |

Your OAuth token ID can be found at: `https://app.terraform.io/app/[YOUR ORG]/settings/version-control`. You may wish to copy and store this as a GitHub encrypted secret.

## Outputs

The action generates no outputs.

## Example Usage

Examples assume variables stored as GitHub [encrypted secrets][].

Set description, working directory and VCS repository in one step:

```yaml
- name: Update workspace settings
    uses: cbsinteractive/update-tfc-workspace-action@v2
    with:
        tfcToken: ${{ secrets.tfc_org_token }}
        orgName: ${{ secrets.tfc_org }}
        workspaceName: some-tfc-workspace-name
        setDescription: some description
        setWorkingDirectory: terraform
        setVCSIdentifier: some-org/some-repo
        setVCSBranch: some-branch
        setVCSOAuthTokenID: ${{ secrets.tfc_oauth_token_id }}
```

Unset VCS repository:

```yaml
- name: Detach workspace VCS repo
    uses: cbsinteractive/update-tfc-workspace-action@v2
    with:
        tfcToken: ${{ secrets.tfc_org_token }}
        orgName: ${{ secrets.tfc_org }}
        workspaceName: some-tfc-workspace-name
        unsetVCSIdentifier: true
        unsetVCSBranch: true
        unsetVCSOAuthTokenID: true
```

## Development

Setup the dev environment:

```shell
make setup-venv
```

Format the Python:

```shell
make format
```

Lint the Python:

```shell
make lint
```

Run Python unit tests:

```shell
make test
```

[encrypted secrets]: https://docs.github.com/en/actions/reference/encrypted-secrets
