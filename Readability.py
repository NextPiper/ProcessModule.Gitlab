import math
import re as regex

# Local imports
from CodeSummary import CodeSummary
from LanguageDescriptor import LanguageDescriptor

# String identifier constants and a constant to determine that weight in a linear combination scenario
from MethodInfo import MethodInfo

AVG_LINE_LENGTH = "average_line_length"
AVG_LINE_CONST = 1.0

FILE_LENGTH ="class_length"
FILE_LENGTH_CONST = 1.0

SYMBOL_RATIO = "symbol_ratio"
SYMBOL_CONST = 20.0

CODE_BLOCK_SIZE = "code_block_size"
CODE_BLOCK_CONST = 1.0

UNCOMMETEDMETHODS = "uncommented_method"
UNCOMMETEDMETHODS_CONST = 1.0

TOKEN_REGEX = regex.compile(r'(\W+)', flags=regex.UNICODE)

class CodeAnalyser:

    def __init__(self, language_Descriptor):
        self.language_Descriptor = language_Descriptor

    def compute_code_score(self, filePath):
        # Open the filePath
        file = open(filePath, "r")
        # Read the code from the file
        code = file.read()
        # break the file up into array of lines with break on ("\n")
        lines = code.split('\n')
        # Pass the lines array an compute a detailed score
        score_dic = self.compute_detailed_code_score(code, lines)

        return CodeSummary(score_dic)

    # Calls different code metrics and performs an analyses
    def compute_detailed_code_score(self, code, lines):

        # ****** Calculate code readability & Maintainability sections ******
        avg_line_length = self.computeAverageLineLength(lines, True)
        file_length_penalty = self.file_length_penalty(lines)
        symbol_score = self.symbol_score(code, lines)
        block_score = self.compute_average_code_block_size(lines)
        methodcomments = self.compute_amount_of_ucommented_methods(lines)
        method_info_list = self.compute_method_info(lines)

        #*********** Calculate average of the parameters in method info ***********
        avg_comment_ratio= self.average_out_commentratio(method_info_list)
        avg_parameter_length = self.average_out_parameterlenght(method_info_list)

        # ****** Store the different metric ******
        details = {}
        # Add code metrics to dictionary with string identifier and a weigthed valube based on a constant.
        details[AVG_LINE_LENGTH] = avg_line_length * AVG_LINE_CONST
        details[FILE_LENGTH] = file_length_penalty * FILE_LENGTH_CONST
        details[SYMBOL_RATIO] = symbol_score * SYMBOL_CONST
        details[CODE_BLOCK_SIZE] = block_score * CODE_BLOCK_CONST
        details[UNCOMMETEDMETHODS] = methodcomments * UNCOMMETEDMETHODS_CONST

        return details

    # Get the average line length
    def computeAverageLineLength(self, lines, ignoreComments=False):
        # First Calculate the sum of all lines
        ignoredLines = 0
        sum = 0
        for line in lines:
            if (ignoreComments):
                if self.language_Descriptor.is_Comment(line):
                    ignoredLines += 1
                    continue
            sum += len(line)
        return sum / (len(lines) - ignoredLines)

    # Cost function of long classes
    def file_length_penalty(self, lines, alowed_growth = 12):
        number_lines = len(lines)

        if(math.sqrt(number_lines) - alowed_growth) < 0:
            return math.sqrt(number_lines)

        if math.pow(math.sqrt(number_lines) - alowed_growth, 2) > math.sqrt(number_lines):
            return math.pow(math.sqrt(number_lines)- alowed_growth, 2)
        else:
            return math.sqrt(number_lines)

    # Calculate the average ratio of symbols to total tokens pr.line
    def symbol_score(self, code, lines):

        # Accumulate the code score
        accumulatedSymbolRatioPrLine = 0.0

        for line in lines:
            # Break each line into tokens. A token is any symbol, non-word, word
            # using Microsoft.AspNet.Core; --> ["Using", " ", "Microsoft", ".", "AspNet", ".", "Core", ";"]
            line_tokens = TOKEN_REGEX.split(line)
            tokens = []
            for token in line_tokens:
                for char in token.split():
                    if(len(char) != 0):
                        tokens.append(token)

            # Retreive the number of symbols from line
            numberOfSymbols = 0
            for token in tokens:
                match = TOKEN_REGEX.match(token)
                if match:
                    numberOfSymbols += len(match.group(0)) == len(token)

            numberOfNoneSymbols = 0
            for token in tokens:
                match = TOKEN_REGEX.match(token)
                if not match:
                    numberOfNoneSymbols += 1

            accumulatedSymbolRatioPrLine += numberOfSymbols / float(max(1, numberOfSymbols + numberOfNoneSymbols))

        # Computes the average ratio of symbols to total tokens pr line
        return accumulatedSymbolRatioPrLine / max(1, len(lines))

    # Compute the average number of lines for each block of code. Blocks consists of consecutive lines
    # without any whitespace or other line breaking charecters suchs as if, do, { , }
    def compute_average_code_block_size(self, lines):
        blocks = []
        currentBlockSize = 0
        for line in lines:
            if len(line.strip()) <= 3:
                if currentBlockSize > 0:
                    blocks.append(currentBlockSize)
                currentBlockSize = 0
            else:
                currentBlockSize += 1
        if currentBlockSize > 0:
            blocks.append(currentBlockSize)

        # Compute the average lines_per_block
        sum = 0.0
        for block in blocks:
            sum += block
        return sum / float(max(1, len(blocks)))

    def compute_amount_of_ucommented_methods(self, lines):
        methods = 0
        methodcomment = 0
        previousLine = None
        for line in lines:
            if self.language_Descriptor.is_Method(line):
                methods += 1
                if self.language_Descriptor.is_Comment(previousLine):
                    methodcomment += 1
            lineStrip = line.strip()
            if not lineStrip == '':
                previousLine = line
        uncommentedMethods = methods - methodcomment
        print(uncommentedMethods)
        return uncommentedMethods

    def compute_method_info(self, lines):

        methods = []
        methodInfo = None

        for line in lines:

            if (self.language_Descriptor.is_Method(line)):
                # Encountered a method, create methodInfo object and close previous method
                if methodInfo:
                    methods.append(methodInfo)
                    methodInfo.compute_comment_ratio()
                    methodInfo = None
                # Create next method info object
                methodInfo = MethodInfo(line, self.language_Descriptor)
                continue

            if(methodInfo):
                if methodInfo.isClosed:
                    methods.append(methodInfo)
                    methodInfo.compute_comment_ratio()
                    methodInfo = None
                else:
                    methodInfo.readLine(line)

        return methods

    def average_out_commentratio(self, methodInfoList):
        sumofcommentratio = 0
        for methodinfo in methodInfoList:
            sumofcommentratio += methodinfo.commentRatio
        return sumofcommentratio/len(methodInfoList)

    def average_out_parameterlenght(self, methodInfoList):
        sumofparameterlength = 0
        amountofparametes = 0
        for methodinfo in methodInfoList:
            if len(methodinfo.parameterList) != 0:
                sumofparameterlength += len(methodinfo.parameterList)
                amountofparametes += 1
        return sumofparameterlength/amountofparametes



if __name__ == '__main__':

    file = "/Users/magnus/Documents/GitHub/NextPipe/NextPipe.Core/Domain/Kubernetes/RabbitMQ/RabbitDeploymentManager.cs"
    #file = "/Users/ulriksandberg/Projects/NextPipe/NextPipe/NextPipe.Core/Events/Handlers/ModulesEventHandler.cs"
    #file = "/Users/ulriksandberg/Projects/NextPipe/NextPipe/NextPipe.Core/Commands/Handlers/BackgroundProcessCommandHandler.cs"
    #file = "/Users/ulriksandberg/Projects/NextPipe/NextPipe/NextPipe.Core/Domain/Kubernetes/RabbitMQ/RabbitDeploymentManager.cs"
    #file = "/Users/ulriksandberg/Projects/NextPipe/NextPipe/NextPipe/Controllers/ModuleController.cs"

    languageDescriptor = LanguageDescriptor(
        lang_prefix=".cs",
        commentTokens=["//", "/*"])

    analyser = CodeAnalyser(languageDescriptor)

    codeSummary = analyser.compute_code_score(file)

    print(codeSummary.getDetailedScoreDic())
    print(codeSummary.getAccumulatedScore())