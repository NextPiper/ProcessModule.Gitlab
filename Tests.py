import unittest
import Readability as Codeanalyser
import LanguageDescriptor as Languagedescriptor


class TestClass(unittest.TestCase):

    TestLanguagedescriptor = Languagedescriptor.LanguageDescriptor(
        lang_prefix=".cs",
        commentTokens=["//", "/*"],
        methodOperators=['if', 'else', 'do', 'while', 'for', 'foreach', 'catch', 'try', 'get', 'set'])

    codeanalyser = Codeanalyser.CodeAnalyser(TestLanguagedescriptor)
    Testlines = 1
    CsharpMethod = "public void test(parameter1 p1, parameter2 p2)"
    Notmethod = "int testinteger = 0;"

    CsharpClass = ["[HttpPost]", "[Route("")]", "public async Task<IActionResult> InstallModule(string imageName, int amountOfReplicas, string moduleName, LoadBalancerConfigRM needLoadBalancer)" ,"{"
                   "var result = ", "await RouteAsync<RequestInstallModule, TaskRequestResponse>(", "new RequestInstallModule(imageName, amountOfReplicas, moduleName, MapLoadBalancerConfig(needLoadBalancer)));",
                   "if (result.IsSuccessful)", "{", "return StatusCode(202, new {monitorUrl = $core/tasks/{result.Id}, msg = result.Message});", "}", "return StatusCode(409, result.Message);", "return StatusCode(409, result.Message);",
                   "return StatusCode(409, result.Message);", "}]"]

    def test_is_method(self):
        self.assertTrue(self.TestLanguagedescriptor.is_Method(self.CsharpMethod))

    def test_fail_is_method(self):
        self.assertFalse(self.TestLanguagedescriptor.is_Method(self.Notmethod))

    def test_wrong_file_exeception(self):
        with self.assertRaises(AttributeError):
            self.codeanalyser.compute_code_score(self.Testlines)

    def test_expected_outcome_block_size(self):
        i = round(self.codeanalyser.compute_average_code_block_size(self.CsharpClass),2)
        self.assertAlmostEqual(i, 3.70,delta=0.1)



if __name__ == '__main__':
    unittest.main()
