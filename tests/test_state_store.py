import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from wordpress_ai_automation.models import TopicRecord
from wordpress_ai_automation.state_store import CSVStateStore


class StateStoreTest(unittest.TestCase):
    def test_state_store_creates_file_and_pending_rows(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "topics.csv"
            store = CSVStateStore(str(path))
            rows = [
                TopicRecord(topic="A", status="Generate"),
                TopicRecord(topic="B", status="Published"),
                TopicRecord(topic="C", status="Error"),
            ]
            store.save(rows)

            loaded = store.load()
            pending = store.pending(loaded, 5)

            self.assertEqual(2, len(pending))
            self.assertEqual("A", pending[0].topic)
            self.assertEqual("C", pending[1].topic)


if __name__ == "__main__":
    unittest.main()
