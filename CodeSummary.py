class CodeSummary:

    def __init__(self, details_dic):
        self.details_dic = details_dic
        self.baseScoreIdentifiers = []

    def addBaseScoreIdentifier(self, identifier):
        self.baseScoreIdentifiers.append(identifier)

    def getAccumulatedScore(self):
        score = 0
        for key in self.details_dic:
            score += self.details_dic[key]
        return score

    def getBaseScore(self):
        baseScore = 0
        for bsId in self.baseScoreIdentifiers:
            baseScore += self.details_dic[bsId]
        return baseScore

    def getDetailedScoreDic(self):
        return self.details_dic