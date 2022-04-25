import os
from unittest.mock import call, patch

import pytest

from entrypoint import run


def _make_environment_variables(overrides):
    result = {
        "INPUT_TFCTOKEN": "some-token",
        "INPUT_ORGNAME": "some-org",
        "INPUT_WORKSPACENAME": "some-workspace",
        "INPUT_SETDESCRIPTION": "",
        "INPUT_SETWORKINGDIRECTORY": "",
        "INPUT_SETVCSIDENTIFIER": "",
        "INPUT_SETVCSBRANCH": "",
        "INPUT_SETVCSOAUTHTOKENID": "",
        "INPUT_SETAPPLYMETHOD": "",
        # GitHub Action presents unset options as "false" if not given
        "INPUT_UNSETDESCRIPTION": "false",
        "INPUT_UNSETWORKINGDIRECTORY": "false",
        "INPUT_UNSETVCSIDENTIFIER": "false",
        "INPUT_UNSETVCSBRANCH": "false",
        "INPUT_UNSETVCSOAUTHTOKENID": "false",
    }
    result.update(overrides)
    return result


@patch("entrypoint.subprocess.check_call")
def test_set_and_unset_description_are_mutually_exclusive(check_call):
    # Code under test
    with patch.dict(
        os.environ,
        _make_environment_variables(
            {"INPUT_SETDESCRIPTION": "foo", "INPUT_UNSETDESCRIPTION": "true"}
        ),
        clear=True,
    ), pytest.raises(Exception) as excinfo:
        run()

    check_call.assert_not_called()
    assert "setDescription and unsetDescription are mutually exclusive" in str(
        excinfo.value
    ) or "unsetDescription and setDescription are mutually exclusive" in str(
        excinfo.value
    )


@patch("entrypoint.subprocess.check_call")
def test_sets_everything(check_call):
    # Code under test
    with patch.dict(
        os.environ,
        _make_environment_variables(
            {
                "INPUT_SETDESCRIPTION": "some description",
                "INPUT_SETWORKINGDIRECTORY": "some/dir",
                "INPUT_SETVCSIDENTIFIER": "some/repo",
                "INPUT_SETVCSBRANCH": "some-branch",
                "INPUT_SETVCSOAUTHTOKENID": "some-token-id",
            }
        ),
        clear=True,
    ):
        run()

    check_call.assert_has_calls(
        [
            call(
                [
                    "/tfc-cli",
                    "workspaces",
                    "set-description",
                    "-token",
                    "some-token",
                    "-org",
                    "some-org",
                    "-workspace",
                    "some-workspace",
                    "-description",
                    "some description",
                ]
            ),
            call(
                [
                    "/tfc-cli",
                    "workspaces",
                    "set-working-directory",
                    "-token",
                    "some-token",
                    "-org",
                    "some-org",
                    "-workspace",
                    "some-workspace",
                    "-working-directory",
                    "some/dir",
                ]
            ),
        ],
        any_order=True,
    )


@patch("entrypoint.subprocess.check_call")
def test_sets_description(check_call):
    # Code under test
    with patch.dict(
        os.environ,
        _make_environment_variables(
            {
                "INPUT_SETDESCRIPTION": "some description",
            }
        ),
        clear=True,
    ):
        run()

    check_call.assert_called_with(
        [
            "/tfc-cli",
            "workspaces",
            "set-description",
            "-token",
            "some-token",
            "-org",
            "some-org",
            "-workspace",
            "some-workspace",
            "-description",
            "some description",
        ]
    )


@patch("entrypoint.subprocess.check_call")
def test_unsets_description(check_call):
    # Code under test
    with patch.dict(
        os.environ,
        _make_environment_variables(
            {
                "INPUT_UNSETDESCRIPTION": "yes",
            }
        ),
        clear=True,
    ):
        run()

    check_call.assert_has_calls(
        [
            call(
                [
                    "/tfc-cli",
                    "workspaces",
                    "unset-description",
                    "-token",
                    "some-token",
                    "-org",
                    "some-org",
                    "-workspace",
                    "some-workspace",
                ]
            )
        ]
    )


@patch("entrypoint.subprocess.check_call")
def test_unsets_working_directory(check_call):
    # Code under test
    with patch.dict(
        os.environ,
        _make_environment_variables({"INPUT_UNSETWORKINGDIRECTORY": "yes"}),
        clear=True,
    ):
        run()

    check_call.assert_has_calls(
        [
            call(
                [
                    "/tfc-cli",
                    "workspaces",
                    "unset-working-directory",
                    "-token",
                    "some-token",
                    "-org",
                    "some-org",
                    "-workspace",
                    "some-workspace",
                ]
            )
        ]
    )


@patch("entrypoint.subprocess.check_call")
def test_sets_vcs_repo(check_call):
    # Code under test
    with patch.dict(
        os.environ,
        _make_environment_variables(
            {
                "INPUT_SETVCSIDENTIFIER": "some/repo",
                "INPUT_SETVCSBRANCH": "some-branch",
                "INPUT_SETVCSOAUTHTOKENID": "some-token-id",
            }
        ),
        clear=True,
    ):
        run()

    check_call.assert_called_with(
        [
            "/tfc-cli",
            "workspaces",
            "set-vcs-branch",
            "-token",
            "some-token",
            "-org",
            "some-org",
            "-workspace",
            "some-workspace",
            "-identifier",
            "some/repo",
            "-branch",
            "some-branch",
            "-oauth-token-id",
            "some-token-id",
        ]
    )


@patch("entrypoint.subprocess.check_call")
def test_catches_unset_vars_unparsable_as_bool(check_call):
    # Code under test
    with patch.dict(
        os.environ,
        _make_environment_variables(
            {
                "INPUT_UNSETDESCRIPTION": "freddy monkeypants",
            }
        ),
        clear=True,
    ), pytest.raises(Exception) as excinfo:
        run()

    assert (
        'If an "unset" variable is specified, it must have a'
        ' value parsable as boolean (got "freddy monkeypants")' in str(excinfo.value)
    )


@patch("entrypoint.subprocess.check_call")
def test_vcs_settings_are_mutually_necessary(check_call):
    test_configs = [
        (
            {
                "INPUT_SETVCSIDENTIFIER": "foo",
            },
        ),
        (
            {
                "INPUT_SETVCSBRANCH": "foo",
            },
        ),
        (
            {
                "INPUT_SETVCSOAUTHTOKENID": "foo",
            },
        ),
    ]
    for config in test_configs:
        # Code under test
        with patch.dict(
            os.environ,
            _make_environment_variables(config[0]),
            clear=True,
        ), pytest.raises(Exception) as excinfo:
            run()

        check_call.assert_not_called()
        assert "setVCS* variables are mutually necessary" in str(excinfo.value)


@patch("entrypoint.subprocess.check_call")
def test_can_set_apply_method_to_auto(check_call):
    # Code under test
    with patch.dict(
        os.environ,
        _make_environment_variables(
            {
                "INPUT_SETAPPLYMETHOD": "auto",
            }
        ),
        clear=True,
    ):
        run()

    check_call.assert_called_with(
        [
            "/tfc-cli",
            "workspaces",
            "set-apply-method",
            "-token",
            "some-token",
            "-org",
            "some-org",
            "-workspace",
            "some-workspace",
            "-method",
            "auto",
        ]
    )
