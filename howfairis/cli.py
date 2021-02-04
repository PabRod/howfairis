import os
import sys
import click
from colorama import init as init_terminal_colors
from howfairis import Checker
from howfairis import Config
from howfairis import Repo
from howfairis import __version__
from howfairis.compliance import Compliance


# pylint: disable=too-many-arguments
@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("-b", "--branch", default=None, type=click.STRING,
              help="Which git branch to use. Also accepts other git references like SHA or tag.")
@click.option("-c", "--config-file", default=None, type=click.Path(),
              help="Name of the configuration file to control howfairis'es behavior. The configuration " +
                   "file needs to be present on the local system and can include a relative path.")
@click.option("-d", "--show-default-config", default=False, is_flag=True,
              help="Show default configuration and exit.")
@click.option("-i", "--ignore-remote-config", default=False, is_flag=True,
              help="Ignore any configuration files on the remote.")
@click.option("-p", "--path", default=None, type=click.STRING,
              help="Relative path (on the remote). Use this if you want howfairis to look for a " +
                   "README and a configuration file in a subdirectory.")
@click.option("-r", "--remote-config-file", default=None, type=click.STRING,
              help="Name of the configuration file to control howfairis'es behavior. The configuration " +
                   "file needs to be on the remote, and takes into account the value of " +
                   "--branch and --path. Default: .howfairis.yml")
@click.option("-t", "--show-trace", default=False, is_flag=True,
              help="Show full traceback on errors.")
@click.option("-v", "--version", default=False, is_flag=True,
              help="Show version and exit.")
@click.argument("url", required=False)
def cli(url=None, branch=None, config_file=None, remote_config_file=None, path=None,
        show_trace=False, version=False, ignore_remote_config=False, show_default_config=False):
    # pylint: disable=too-many-locals

    """Determine compliance with recommendations from fair-software.eu for the GitHub or GitLab repository at URL."""

    if version is True:
        print("version: {0}".format(__version__))
        return

    if show_default_config is True:
        pkg_root = os.path.dirname(__file__)
        config_filename = os.path.join(pkg_root, "data", ".howfairis.yml")
        with open(config_filename, "rt") as f:
            text = f.read()
        print(text)
        return

    if show_trace is False:
        sys.tracebacklimit = 0

    init_terminal_colors()
    assert url is not None, "Expected URL to not be emtpy."
    print("Checking compliance with fair-software.eu...")

    if url is not None:
        print("url: " + url)

    if branch is not None:
        print("branch: " + branch)

    if path is not None:
        print("path: " + path)

    if ignore_remote_config is True:
        print("Ignoring any configuration files on the remote.")
        assert remote_config_file is None, "When ignoring any configuration files on the remote, you" + \
                                           " should not set a remote configuration filename."
    else:
        if remote_config_file is not None:
            print("Remote configuration filename: " + remote_config_file)

    if config_file is not None:
        print("Local configuration file: " + config_file)

    repo = Repo(url, branch, path, remote_config_file)
    config = Config(repo, config_file, ignore_remote_config)

    checker = Checker(config, repo)
    checker.check_five_recommendations()

    print("\nCalculated compliance: " + " ".join(checker.compliance.as_unicode()) + "\n")

    if checker.readme.text is None:
        sys.exit(1)

    readme_badge_found, readme_badge_compliance = get_fair_software_badge(checker.readme.text)

    if not readme_badge_found:
        print("It seems you have not yet added the fair-software.eu badge to " +
              "your {0}. You can do so by pasting the following snippet:\n\n{1}"
              .format(checker.readme.filename, checker.badge))
        sys.exit(1)

    if checker.compliance == readme_badge_compliance:
        print("Expected badge is equal to the actual badge. It's all good.\n")
        sys.exit(0)

    if checker.compliance > readme_badge_compliance:
        print("Congratulations! The compliance of your repository exceeds " +
              "the current fair-software.eu badge in your " +
              "{0}. You can replace it with the following snippet:\n\n{1}"
              .format(checker.readme.filename, checker.badge))
        sys.exit(1)

    print("The compliance of your repository is different from the current " +
          "fair-software.eu badge in your " +
          "{0}. Please replace it with the following snippet:\n\n{1}"
          .format(checker.readme.filename, checker.badge))

    sys.exit(1)


def get_fair_software_badge(text):
    url = "https://img.shields.io/badge/fair--software.eu"
    url_location = text.find(url)
    if url_location < 0:
        return(False, Compliance())
    start_id = url_location+len(url)+1
    return(True, Compliance.urldecode(text[start_id:start_id+69]))


if __name__ == "__main__":
    cli()
