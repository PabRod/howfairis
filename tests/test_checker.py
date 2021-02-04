import pytest
from requests_mock import Mocker

from howfairis import Repo, Config, Checker
from howfairis.compliance import Compliance
from howfairis.readme import Readme


@pytest.fixture
def badghurl_checker(requests_mock: Mocker):
    requests_mock.get('https://raw.githubusercontent.com/fair-software/does-not-exist/main/.howfairis.yml', status_code=404)
    requests_mock.get('https://raw.githubusercontent.com/fair-software/does-not-exist/main/.howfairis.yml', status_code=404)
    requests_mock.get('https://raw.githubusercontent.com/fair-software/does-not-exist/main/README.md', status_code=404)
    requests_mock.get('https://raw.githubusercontent.com/fair-software/does-not-exist/main/README.rst', status_code=404)
    requests_mock.get('https://api.github.com/repos/fair-software/does-not-exist', status_code=404)
    requests_mock.get('https://api.github.com/repos/fair-software/does-not-exist/license', status_code=404)
    requests_mock.get('https://github.com/fair-software/does-not-exist', status_code=404)
    requests_mock.get('https://raw.githubusercontent.com/fair-software/does-not-exist/main/CITATION', status_code=404)
    requests_mock.get('https://raw.githubusercontent.com/fair-software/does-not-exist/main/CITATION.cff', status_code=404)
    requests_mock.get('https://raw.githubusercontent.com/fair-software/does-not-exist/main/codemeta.json', status_code=404)
    requests_mock.get('https://raw.githubusercontent.com/fair-software/does-not-exist/main/.zenodo.json', status_code=404)

    repo = Repo('https://github.com/fair-software/does-not-exist')
    config = Config(repo)
    checker = Checker(config, repo)
    return checker


def test_checker_badghurl_emptyreadme(badghurl_checker: Checker):
    readme = badghurl_checker.readme

    expected = Readme(filename=None, text=None, fmt=None)
    assert readme == expected


def test_checker_check_five_recommendations(badghurl_checker: Checker):
    compliance = badghurl_checker.check_five_recommendations().compliance

    expected = Compliance(repository=False, license_=False, registry=False, citation=False, checklist=False)
    assert compliance == expected
