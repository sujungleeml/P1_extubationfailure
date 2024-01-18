import sys
import os
import unittest

# access_database.py directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'data_extraction')))

from access_database import main, load_config

class TestDatabaseAccess(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load config file for testing
        cls.config_file_path = os.path.join(os.path.dirname(__file__), '..', 'config.json') 
        cls.dataframes = main(cls.config_file_path)

    def test_database_connection(self):
        # Test if dataframes are returned
        self.assertIsNotNone(self.dataframes, "Failed to retrieve dataframes")
        self.assertIsInstance(self.dataframes, dict, "Returned dataframes should be in a dictionary")

    def test_specific_table_retrieval(self):
        # Test if a specific table is retrieved correctly
        self.assertIn('patients', self.dataframes, "Patients table not found in returned dataframes")
        patients_df = self.dataframes['patients']
        self.assertFalse(patients_df.empty, "Patients dataframe is empty")

if __name__ == '__main__':
    unittest.main()
