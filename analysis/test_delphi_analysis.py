"""python -m unittest discover analysis"""
import unittest

import delphi_analysis as d


class DelphiAnalysisTest(unittest.TestCase):
    def test_items_parsed_from_survey(self):
        items, domains = d.load_items()
        ids = [it.id for it in items]
        self.assertEqual(list(domains), ["1", "2", "3", "4", "5"])
        self.assertEqual(len(ids), len(set(ids)), "문항 번호 중복")
        self.assertIn("1.1.1", ids)
        self.assertIn("D5", ids)

    def test_quartiles_match_spss(self):
        # SPSS (HAVERAGE) 기준 1..10 의 사분위수: 2.75, 5.5, 8.25
        self.assertEqual(d.quartiles([float(x) for x in range(1, 11)]), (2.75, 5.5, 8.25))

    def test_cvr_consensus_convergence(self):
        it = d.Item("x", "x", "1")
        s = d.describe(it, [5, 5, 4, 4, 4, 4, 3, 2, 5, 4])  # 필수(4점 이상) 8/10
        self.assertAlmostEqual(s.cvr, 0.6)
        self.assertAlmostEqual(s.mdn, 4.0)
        self.assertAlmostEqual(s.convergence, (s.q3 - s.q1) / 2)
        self.assertAlmostEqual(s.consensus, 1 - (s.q3 - s.q1) / 4.0)
        self.assertFalse(s.criteria["CVR"])  # N=10 최소 CVR .62

    def test_min_cvr_is_conservative_between_table_rows(self):
        self.assertEqual(d.min_cvr(10), 0.62)
        self.assertEqual(d.min_cvr(17), 0.49)  # 15명 기준값 사용
        self.assertEqual(d.min_cvr(3), 1.0)


if __name__ == "__main__":
    unittest.main()
