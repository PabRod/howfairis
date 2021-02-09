import os
from typing import Optional
import requests
from ruamel.yaml import YAML
from voluptuous.error import Invalid
from voluptuous.error import MultipleInvalid
from howfairis.repo import Repo
from howfairis.schema import validate_against_schema


class Config:
    """Control the behavior of the howfairis package

    Args:
        repo: Repository which is used to fetch config from
        config_filename: Default is ".howfairis.yml"
        ignore_remote_config: If true then does not try to merge config from remote repository.
    """

    def __init__(self, repo: Repo, config_filename: Optional[str] = None, ignore_remote_config: bool = False):
        self._default = Config._load_default_config()
        self._repo = Config._load_repo_config(repo, ignore_remote_config)
        self._user = Config._load_user_config(config_filename)
        self._merged = self._merge_configurations()

    @staticmethod
    def _load_default_config():
        pkg_root = os.path.dirname(__file__)
        config_filename = os.path.join(pkg_root, "data", ".howfairis.yml")
        with open(config_filename, "rt") as f:
            text = f.read()
        default_config = YAML(typ="safe").load(text)
        if default_config is None:
            default_config = dict()
        try:
            validate_against_schema(default_config)
        except (Invalid, MultipleInvalid):
            print(
                "Default configuration file should follow the schema for it to be considered.")
            return dict()
        return default_config

    @staticmethod
    def _load_repo_config(repo, ignore_remote_config):
        if repo is None:
            return dict()

        if ignore_remote_config is True:
            return dict()

        if repo.config_file is None:
            config_filename = ".howfairis.yml"
        else:
            config_filename = repo.config_file

        raw_url = repo.raw_url_format_string.format(config_filename)
        try:
            response = requests.get(raw_url)
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
            print("Using the configuration file {0}".format(raw_url))
        except requests.HTTPError as e:
            if repo.config_file is not None:
                raise Exception(
                    "Could not find the configuration file {0}".format(raw_url)) from e
            return dict()

        try:
            repo_config = YAML(typ="safe").load(response.text)
        except Exception as e:
            raise Exception(
                "Problem loading YAML configuration from file {0}".format(raw_url)) from e

        try:
            validate_against_schema(repo_config)
        except (Invalid, MultipleInvalid):
            print(
                "Repository's configuration file should follow the schema for it to be considered.")
            return dict()

        return repo_config

    @staticmethod
    def _load_user_config(config_filename):
        if config_filename is None:
            return dict()

        p = os.path.join(os.getcwd(), config_filename)
        if not os.path.exists(p):
            raise FileNotFoundError(
                "{0} doesn't exist.".format(config_filename))

        with open(p, "rt") as f:
            text = f.read()
        user_config = YAML(typ="safe").load(text)
        if user_config is None:
            user_config = dict()
        try:
            validate_against_schema(user_config)
        except Exception as e:
            raise Exception(
                "User configuration file should follow the schema.") from e
        return user_config

    def _merge_configurations(self):
        """Configuration dictionary based on merger of

            * default config from this package
            * config from repository
            * config from local user
        """
        m = dict()
        m.update(self._default)
        m.update(self._repo)
        m.update(self._user)
        return m

    @property
    def force_repository(self):
        """Forces recommendation to be compliant or non-compliant.
        If set to True/False then checks for that recommendation are bypassed and not executed."""
        return self._merged.get("force_repository")

    @property
    def force_license(self):
        """Forces recommendation to be compliant or non-compliant.
        If set to True/False then checks for that recommendation are bypassed and not executed."""
        return self._merged.get("force_license")

    @property
    def force_registry(self):
        """Forces recommendation to be compliant or non-compliant.
        If set to True/False then checks for that recommendation are bypassed and not executed."""
        return self._merged.get("force_registry")

    @property
    def force_citation(self):
        """Forces recommendation to be compliant or non-compliant.
        If set to True/False then checks for that recommendation are bypassed and not executed."""
        return self._merged.get("force_citation")

    @property
    def force_checklist(self):
        """Forces recommendation to be compliant or non-compliant.
        If set to True/False then checks for that recommendation are bypassed and not executed."""
        return self._merged.get("force_checklist")

    @property
    def include_comments(self):
        """Whether while reading the README of a repository the comments in it should be included."""
        return self._merged.get("include_comments")
