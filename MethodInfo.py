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

        lineSplit = line.split()
        if len(lineSplit) != 0:
            self.methodLength += 1
        for char in line:
            if char == '{':
                self.indentation.append('{')
                self.add_node()
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

    def backtrack_method_tree(self):
        self.methodTreeCursor = self.methodTreeCursor.get_parent()

    def initialize_method_tree(self):
        self.methodTreeCursor = Node(None)
        self.methodTreeRoot = self.methodTreeCursor

    def add_node(self):
        node = Node(self.methodTreeCursor)
        self.methodTreeCursor.appendChild(node)
        self.methodTreeCursor = node

    def get_method_tree(self):
        return self.methodTreeRoot

class Node:

    def __init__(self, parent_node):
        self.parent_node = parent_node
        self.childrens = []

    def appendChild(self, node):
        self.childrens.append(node)

    def get_parent(self):
        return self.parent_node