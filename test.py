import unittest
from Drive_Information import drive_information as di
from types import SimpleNamespace
from queue import Queue

class tests(unittest.TestCase):
    def setUp(self):
        self.obj = di.__new__(di)

    def test_initialize_queues(self):
        sample_drives = [SimpleNamespace(device="A:\\"), SimpleNamespace(device="B:\\")]
        q = Queue()
        self.obj.initialize_queue(sample_drives, q)
        actual = []
        while not q.empty():
            actual.append(q.get())

        self.assertCountEqual(actual, [("A:\\", "A:\\"), ("B:\\", "B:\\")])
        
if __name__ == "__main__":
    unittest.main(verbosity=2)
