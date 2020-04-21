import regex


class LanguageDescriptor:

    cSharpMethod = regex.compile(
        r'\b(public|private|internal|protected)\s*(static|virtual|abstract)?\s*[a-zA-Z<>]*\s[a-zA-Z1-9_<>]+\s?\s*[a-zA-Z1-9<>_]*\((([a-zA-Z1-9_="_:,\[\]\<\>]*\s*[a-zA-Z1-9_=",:_]*\s*)[,]?\s*)+\)')
    reDictonary = {'.cs': cSharpMethod }

    def __init__(self, lang_prefix, commentTokens, methodOperators):
        self.lang_prefix = lang_prefix
        self.commentTokens = commentTokens
        self.methodOperators = methodOperators

    def is_Comment(self, line):
        stripLine = line.strip()
        for token in self.commentTokens:
            if stripLine.startswith(token):
                return True
        return False

    def is_Method(self, line):
        re = self.reDictonary.get(self.lang_prefix)
        stripLine = line.strip()
        match = re.search(stripLine)
        if match:
            return True
        return False

    def identify_operator(self, line):
        for methodOperator in self.methodOperators:
            if line.find(methodOperator) != -1:
                return methodOperator
        return None