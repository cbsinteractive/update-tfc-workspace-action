# Update TFC Workspace

A GitHub Action used to update Terraform Cloud workspaces.

## Inputs

The action expects the following inputs:

| Variable           | Required | Description                                                                 |
| ------------------ | -------- | --------------------------------------------------------------------------- |
| `tfcToken`         | Yes      | A Terraform Cloud API token with access to manage the workspace             |
| `orgName`          | Yes      | The name of the Terraform Cloud organization in which the workspace resides |
| `workspaceName`    | Yes      | The name of the Terraform Cloud workspace to manage                         |
| `description`      | Yes      | The workspace description                                                   |
| `vcsIdentifier`    | Yes      | The VCS repo to connect, e.g. some-org/some-repo                            |
| `vcsBranch`        | Yes      | The VCS repo branch to connect                                              |
| `vcsOAuthTokenID`  | Yes      | The OAuth token ID used to authorize the connection                         |
| `workingDirectory` | Yes      | The directory that Terraform will execute within                            |

At this time, the action can only be used to set values to non-empty strings. In other words, the ability to "unset" settings is not yet supported.

Your OAuth token ID can be found at: `https://app.terraform.io/app/[YOUR ORG]/settings/version-control`. You may wish to copy and store this as a GitHub encrypted secret.

## Outputs

The action generates no outputs.

## Example Usage

```yaml
- name: Update workspace settings
    uses: cbsinteractive/update-tfc-workspace-action@v1
    with:
        tfcToken: ${{ secrets.tfc_org_token }}
        orgName: ${{ secrets.tfc_org }}
        workspaceName: some-tfc-workspace-name
        description: some description
        vcsIdentifier: some-org/some-repo
        vcsBranch: some-branch
        vcsOAuthTokenID: ${{ secrets.tfc_oauth_token_id }}
        workingDirectory: terraform
```

This example assumes variables stored as GitHub [encrypted secrets][].

[encrypted secrets]: https://docs.github.com/en/actions/reference/encrypted-secrets
