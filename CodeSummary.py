class CodeSummary:

    def __init__(self, details_dic):
        self.details_dic = details_dic

    def getAccumulatedScore(self):
        score = 0
        for key in self.details_dic:
            score += self.details_dic[key]
        return score

    def getDetailedScoreDic(self):
        return self.details_dic