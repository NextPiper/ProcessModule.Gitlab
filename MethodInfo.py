import re as regex
import enum
TOKEN_REGEX = regex.compile(r'(\W+)', flags=regex.UNICODE)

class MethodInfo:

    def __init__(self, methodDeclaration, language_descriptor):
        self.methodDeclaration = methodDeclaration
        self.parameterList = []
        self.isClosed = False
        self.language_descriptor = language_descriptor

        self.indentation = []
        self.methodLength = 0
        self.linesOfComments = 0
        self.commentRatio = 0

        self.methodTreeRoot = None
        self.methodTreeCursor = None
        self.previousLine = None
        self.methodFlowDetails = None

        # Analyse the method declaration and rea number of parameters
        self.analyseNumberOfParameters()
        # Calculate score of ratio between comment and length of method

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
            if self.language_descriptor.is_Comment(line):
                self.linesOfComments += 1
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
            line = str(self.previousLine) + str(originLine)

        node = Node(self.methodTreeCursor, line)
        self.methodTreeCursor.appendChild(node)
        self.methodTreeCursor = node

    def get_method_tree(self):
        return self.methodTreeRoot

    def compute_comment_ratio(self):
        if self.methodLength != 0 and self.linesOfComments != 0:
            self.commentRatio = self.methodLength / self.linesOfComments
        if self.methodLength != 0 and self.linesOfComments == 0:
            self.commentRatio = self.methodLength

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

    def walk_tree(self):
        node_cursor = self.methodTreeRoot
        methodFlowDetails = MethodFlowDetails()
        self.methodFlowDetails = self.walk_tree_rec(node_cursor, methodFlowDetails)

    def walk_tree_rec(self, node, methodFlowDetails):

        # setDepthOfCurrenNode as details
        methodFlowDetails.set_Depth(node.get_depth())
        find_flow_keyword = self.find_flow_keyword(node.originLine)
        if find_flow_keyword:
            methodFlowDetails.set_methodOperator(find_flow_keyword, node.get_depth())

        for child in node.childrens:
            self.walk_tree_rec(child, methodFlowDetails)

        return methodFlowDetails

    def find_flow_keyword(self, line):
        if line:
            return self.language_descriptor.identify_operator(line)
        return None

class Node:

    def __init__(self, parent_node, originLine):
        self.parent_node = parent_node
        self.childrens = []
        self.originLine = originLine
        if parent_node:
            self.depth = parent_node.get_depth() + 1
        else:
            self.depth = 0

    def appendChild(self, node):
        self.childrens.append(node)

    def get_parent(self):
        return self.parent_node

    def get_depth(self):
        return self.depth


class MethodFlowDetails:

    def __init__(self):
        self.depth = 0
        self.methodOperators = []

    def set_Depth(self, depth):
        if self.depth < depth:
            self.depth = depth

    def set_methodOperator(self, methodOperator, depth):
        self.methodOperators.append(MethodOperator(methodOperator, depth))

class MethodOperator:

    def __init__(self, methodOperator, depth):
        self.methodOperator = methodOperator
        self.depth = depth