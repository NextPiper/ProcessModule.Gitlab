import re as regex

TOKEN_REGEX = regex.compile(r'(\W+)', flags=regex.UNICODE)

class MethodInfo:

    def __init__(self, methodDeclaration):
        self.methodDeclaration = methodDeclaration
        self.parameterList = []
        self.isClosed = False

        self.indentation = []
        self.methodLength = 0

        self.methodTreeRoot = None
        self.methodTreeCursor = None
        self.previousLine = None

        # Analyse the method declaration and rea number of parameters
        self.analyseNumberOfParameters()

    def analyseNumberOfParameters(self):

        parameters = []
        currentParameter = ''
        methodParameterStartFound = False

        for char in self.methodDeclaration:
            # End loop if end parenthese has been found
            if (char == ')'):
                if not currentParameter.isspace() or currentParameter == '':
                    parameters.append(currentParameter)
                break
            # Start counting
            if(char == '('):
                methodParameterStartFound = True
                continue

            if(methodParameterStartFound):
                if char != ',':
                    currentParameter += char
                else:
                    parameters.append(currentParameter)
                    currentParameter = ""

        self.parameterList = parameters
        self.initialize_method_tree()
        self.readLine(self.methodDeclaration)


    def readLine(self, line):

        inComment = False

        lineSplit = line.split()
        if len(lineSplit) != 0:
            self.methodLength += 1
        for char in line:
            if char == "\"" or char == "\'":
                if inComment:
                    inComment = False
                else:
                    inComment = True
                continue
            if inComment:
                continue
            if char == '{':
                self.indentation.append('{')
                self.add_node(line)
            if char == '}':
                self.backtrack_method_tree()
                # Check if we can remove an in item
                if len(self.indentation) == 0:
                    self.isClosed = True
                    break
                else:
                    self.indentation.pop(len(self.indentation) -1)
                    if len(self.indentation) == 0:
                        self.isClosed = True
                        break
        self.previousLine = line

    def backtrack_method_tree(self):
        self.methodTreeCursor = self.methodTreeCursor.get_parent()

    def initialize_method_tree(self):
        self.methodTreeCursor = Node(None, None)
        self.methodTreeRoot = self.methodTreeCursor

    def add_node(self, originLine):

        line = originLine
        if self.previousLineInfoRequired(originLine):
            line = self.previousLine + originLine

        node = Node(self.methodTreeCursor, line)
        self.methodTreeCursor.appendChild(node)
        self.methodTreeCursor = node

    def get_method_tree(self):
        return self.methodTreeRoot

    def previousLineInfoRequired(self, line):

        prevChar = ""
        tokens = TOKEN_REGEX.split(line)

        for token in tokens:
            splitToken = token.split()
            if len(splitToken) != 0:

                # We reached the start check if there where any prevChar
                if token[0] == "{" :
                    if len(prevChar) == 0:
                        return True
                    else:
                        return False
                prevChar += token[0]
        return True

class Node:

    def __init__(self, parent_node, originLine):
        self.parent_node = parent_node
        self.childrens = []
        self.originLine = originLine

    def appendChild(self, node):
        self.childrens.append(node)

    def get_parent(self):
        return self.parent_node