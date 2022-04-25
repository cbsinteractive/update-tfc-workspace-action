import os
import subprocess
from collections.abc import Iterable, Mapping
from distutils.util import strtobool
from itertools import groupby
from operator import attrgetter
from typing import Any, Callable, Optional


class VariableSpec:
    def __init__(
        self,
        action_variable: str,
        variable_type: str = None,
        cli_subcommand: str = None,
        cli_variable: str = None,
        mutually_exclusive_vars: Iterable[str] = (),
        mutually_necessary_vars: Iterable[str] = (),
        data_type: type = None,
        allowed_values: Iterable[str] = (),
        from_value_fun: Callable[[Any], Any] = None,
    ) -> None:
        self.__action_variable = action_variable
        assert variable_type in ["set", "unset", None]
        self.__variable_type = variable_type
        self.__cli_subcommand = cli_subcommand
        self.__cli_variable = cli_variable
        self.__mutually_exclusive_vars = mutually_exclusive_vars
        self.__mutually_necessary_vars = mutually_necessary_vars
        self.__data_type = data_type
        self.__allowed_values = allowed_values
        self.__from_value_fun = from_value_fun

    def __repr__(self) -> str:
        return (
            f"VariableSpec(action_variabler={self.__action_variable}"
            f",cli_subcommand={self.__cli_subcommand}"
            f",variable_type={self.__variable_type}"
            f",data_type={self.__data_type})"
        )

    @property
    def action_variable(self):
        return self.__action_variable

    @property
    def cli_subcommand(self) -> Optional[str]:
        return self.__cli_subcommand

    @property
    def cli_variable(self):
        return self.__cli_variable

    @property
    def variable_type(self):
        return self.__variable_type

    @property
    def mutually_exclusive_vars(self):
        return self.__mutually_exclusive_vars

    @property
    def mutually_necessary_vars(self):
        return self.__mutually_necessary_vars

    @property
    def data_type(self):
        return self.__data_type

    @property
    def allowed_values(self):
        return self.__allowed_values

    def from_value(self, value):
        return self.__from_value_fun(value)

    @property
    def env_var(self):
        """
        Converts from the name the Action user knows to
        the environment variable name created by the GHA runtime.

        Example: setDescription would become INPUT_SETDESCRIPTION
        """
        return f"input_{self.__action_variable}".upper()

    def get_value(self):
        raw_val = os.environ.get(self.env_var)
        if self.__variable_type is None:
            if raw_val is None:
                raise Exception(f"'{self.action_variable}' setting not provided")
            return raw_val
        if self.__variable_type == "set":
            return raw_val
        if self.__variable_type == "unset":
            try:
                return bool(strtobool(raw_val))
            except ValueError:
                raise Exception(
                    'If an "unset" variable is specified, it must have'
                    f' a value parsable as boolean (got "{raw_val}")'
                )


def validate_inputs(
    source_var: VariableSpec, runtime_settings, variables: Iterable[VariableSpec]
) -> None:
    if not _is_variable_specified(source_var, runtime_settings):
        return
    for var_name in source_var.mutually_exclusive_vars:
        corresponding_var = _get_variable_spec(var_name, variables)
        if _is_variable_specified(corresponding_var, runtime_settings):
            raise Exception(
                f"{source_var.action_variable} and {corresponding_var.action_variable} are mutually exclusive"
            )
    for var_name in source_var.mutually_necessary_vars:
        corresponding_var = _get_variable_spec(var_name, variables)
        if not _is_variable_specified(corresponding_var, runtime_settings):
            raise Exception("setVCS* variables are mutually necessary")

    if len(source_var.allowed_values) > 0:
        value = runtime_settings[source_var.action_variable]
        assert value in source_var.allowed_values, (
            f"Error validating {source_var.cli_subcommand}"
            f" {source_var.cli_variable}: {value} not found in {source_var.allowed_values}"
        )


def _get_variable_spec(name: str, variables: Iterable[VariableSpec]) -> VariableSpec:
    return next(x for x in variables if x.action_variable == name)


def _get_variable_specs() -> list[VariableSpec]:
    return [
        VariableSpec("tfcToken"),
        VariableSpec("orgName"),
        VariableSpec("workspaceName"),
        VariableSpec(
            "setDescription",
            "set",
            "set-description",
            "-description",
            ("unsetDescription",),
        ),
        VariableSpec(
            "unsetDescription",
            "unset",
            "unset-description",
            None,
            ("setDescription",),
        ),
        VariableSpec(
            "setApplyMethod",
            "set",
            "set-auto-apply",
            "-auto-apply",
            (),
            (),
            bool,
            ("auto", "manual"),
            lambda x: "true" if x == "auto" else "false",
        ),
        VariableSpec(
            "setWorkingDirectory",
            "set",
            "set-working-directory",
            "-working-directory",
            ("unsetWorkingDirectory",),
        ),
        VariableSpec(
            "unsetWorkingDirectory",
            "unset",
            "unset-working-directory",
            None,
            ("setWorkingDirectory",),
        ),
        VariableSpec(
            "setVCSIdentifier",
            "set",
            "set-vcs-branch",
            "-identifier",
            ("unsetVCSIdentifier", "unsetVCSBranch", "unsetVCSOAuthTokenID"),
            ("setVCSBranch", "setVCSOAuthTokenID"),
        ),
        VariableSpec(
            "setVCSBranch",
            "set",
            "set-vcs-branch",
            "-branch",
            ("unsetVCSIdentifier", "unsetVCSBranch", "unsetVCSOAuthTokenID"),
            ("setVCSIdentifier", "setVCSOAuthTokenID"),
        ),
        VariableSpec(
            "setVCSOAuthTokenID",
            "set",
            "set-vcs-branch",
            "-oauth-token-id",
            ("unsetVCSIdentifier", "unsetVCSBranch", "unsetVCSOAuthTokenID"),
            (
                "setVCSIdentifier",
                "setVCSBranch",
            ),
        ),
        VariableSpec(
            "unsetVCSIdentifier",
            "unset",
            "unset-vcs-branch",
            None,
            ("setVCSIdentifier", "setVCSBranch", "setVCSOAuthTokenID"),
            ("unsetVCSBranch", "unsetVCSOAuthTokenID"),
        ),
        VariableSpec(
            "unsetVCSBranch",
            "unset",
            "unset-vcs-branch",
            None,
            ("setVCSIdentifier", "setVCSBranch", "setVCSOAuthTokenID"),
            ("unsetVCSIdentifier", "unsetVCSOAuthTokenID"),
        ),
        VariableSpec(
            "unsetVCSOAuthTokenID",
            "unset",
            "unset-vcs-branch",
            None,
            ("setVCSIdentifier", "setVCSBranch", "setVCSOAuthTokenID"),
            ("unsetVCSIdentifier", "unsetVCSBranch"),
        ),
    ]


def _is_variable_specified(
    var_spec: VariableSpec, runtime_settings: Mapping[str, str]
) -> bool:
    if var_spec.variable_type == "unset":
        return runtime_settings[var_spec.action_variable] is True

    if var_spec.variable_type == "set" or var_spec.variable_type is None:
        return len(runtime_settings[var_spec.action_variable]) > 0

    raise Exception(f"Unexpected variable type '{var_spec.variable_type}'")


def _gather_cmd_args(
    runtime_settings: Mapping[str, str], variables: Iterable[VariableSpec]
):
    # Group variable specs by CLI subcommand
    by_command = groupby(
        # Sory by CLI subcommand
        sorted(
            # Eliminate variables with no associated CLI subcommand
            filter(
                lambda x: x.cli_subcommand is not None
                and _is_variable_specified(x, runtime_settings),
                variables,
            ),
            key=attrgetter("cli_subcommand"),
        ),
        key=attrgetter("cli_subcommand"),
    )
    for cli_subcommand, var_specs in by_command:
        result = [
            "/tfc-cli",
            "workspaces",
            cli_subcommand,
            "-token",
            runtime_settings["tfcToken"],
            "-org",
            runtime_settings["orgName"],
            "-workspace",
            runtime_settings["workspaceName"],
        ]
        for var_spec in var_specs:
            if var_spec.variable_type == "set":
                if var_spec.data_type == bool:
                    result.append(
                        f"{var_spec.cli_variable}={var_spec.from_value(runtime_settings[var_spec.action_variable])}"
                    )
                else:
                    result.extend(
                        (
                            var_spec.cli_variable,
                            runtime_settings[var_spec.action_variable],
                        )
                    )
        yield result


def run() -> None:
    variables = _get_variable_specs()
    runtime_settings = {}
    for current_var in variables:
        runtime_settings[current_var.action_variable] = current_var.get_value()

    for var_spec in variables:
        validate_inputs(var_spec, runtime_settings, variables)

    for cmd_args in _gather_cmd_args(runtime_settings, variables):
        subprocess.check_call(cmd_args)


if __name__ == "__main__":
    run()
