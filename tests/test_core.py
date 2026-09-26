import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


pothole = module('pothole', 'pothole-detection/pipeline.py')
rag = module('rag', 'mentorai/rag.py')
scale = module('scale', 'autoscaler/simulator.py')


class CoreTests(unittest.TestCase):
    def test_gps_alignment_and_bounds(self):
        points = [pothole.Point(0, 10, 20), pothole.Point(10, 20, 30)]
        self.assertEqual(pothole.interpolate(points, 5).lat, 15)
        self.assertIsNone(pothole.interpolate(points, 11))

    def test_severity_is_area_based(self):
        self.assertEqual(pothole.severity([0, 0, .5, .5]), 'high')

    def test_retrieval_is_persistent_and_cited(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / 'index.db')
            rag.MentorIndex(path).add('career', 'Python supports automation. SQL supports database queries.')
            result = rag.MentorIndex(path).answer('What supports database queries?')
            self.assertIn('SQL', result['answer'])
            self.assertEqual(result['sources'][0]['source'], 'career')

    def test_simulation_accounts_for_load(self):
        result = scale.simulate([100, 200, 300], capacity=100, delay=1)
        self.assertGreater(result['dropped_requests'], 0)
        self.assertEqual(len(result['records']), 3)
        with self.assertRaises(ValueError):
            scale.simulate([-1])


if __name__ == '__main__':
    unittest.main()
