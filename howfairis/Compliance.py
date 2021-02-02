import re
import requests


# pylint: disable=too-many-arguments
class Compliance:
    def __init__(self, repository=None, license_=None, registry=None, citation=None, checklist=None,
                 compliant_symbol="\u25CF", noncompliant_symbol="\u25CB"):
        self._index = 0
        self.repository = repository
        self.license = license_
        self.registry = registry
        self.citation = citation
        self.checklist = checklist
        self.compliant_symbol = compliant_symbol
        self.noncompliant_symbol = noncompliant_symbol

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < 5:
            result = self._state[self._index]
            self._index += 1
            return result
        self._index = 0
        raise StopIteration

    @property
    def _state(self):
        return [self.repository, self.license, self.registry,
                self.citation, self.checklist]

    def as_unicode(self):
        compliance_unicode = [None] * 5
        for i, c in enumerate(self._state):
            if c is True:
                compliance_unicode[i] = self.compliant_symbol
            else:
                compliance_unicode[i] = self.noncompliant_symbol
        return compliance_unicode

    def count(self, value):
        return self._state.count(value)

    def urlencode(self):
        return "%20%20".join([requests.utils.quote(symbol) for symbol in self.as_unicode()])

    def urldecode(self, string):
        compliance_symbols = re.sub(" ", "", requests.utils.unquote(string))
        if len(compliance_symbols) == 5:
            self.repository = (compliance_symbols[0] == self.compliant_symbol)
            self.license = (compliance_symbols[1] == self.compliant_symbol)
            self.registry = (compliance_symbols[2] == self.compliant_symbol)
            self.citation = (compliance_symbols[3] == self.compliant_symbol)
            self.checklist = (compliance_symbols[4] == self.compliant_symbol)
        return(self)

    def __eq__(self, other):
        return \
            self.repository == other.repository and \
            self.license == other.license and \
            self.registry == other.registry and \
            self.citation == other.citation and \
            self.checklist == other.checklist and \
            self.compliant_symbol == other.compliant_symbol and \
            self.noncompliant_symbol == other.noncompliant_symbol

    def __gt__(self, other):
        return \
            (self.repository and not other.repository) or \
            (self.license and not other.license) or \
            (self.registry and not other.registry) or \
            (self.citation and not other.citation) or \
            (self.checklist and not other.checklist)

