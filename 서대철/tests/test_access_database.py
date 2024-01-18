import sys
import os
import unittest

# Adjust the path to include the /src directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'data_extraction')))

from access_database import main, load_config

class TestDatabaseAccess(unittest.TestCase):

    def setUp(self):
        # Setup: Load config file for testing
        self.config_file_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')  # Update with the actual path
        self.config = load_config(self.config_file_path)

    def test_load_config(self):
        # Test if configuration file is loaded correctly
        self.assertIsNotNone(self.config, "Failed to load config file")

    def test_database_connection(self):
        # Test if database connection is established and dataframes are returned
        dataframes = main(self.config_file_path)
        self.assertIsNotNone(dataframes, "Failed to retrieve dataframes")
        self.assertIsInstance(dataframes, dict, "Returned dataframes should be in a dictionary")

    def test_specific_table_retrieval(self):
        # Test if a specific table is retrieved correctly
        dataframes = main(self.config_file_path)
        self.assertIn('patients', dataframes, "Patients table not found in returned dataframes")
        patients_df = dataframes['patients']
        self.assertFalse(patients_df.empty, "Patients dataframe is empty")

        # Add similar tests for other tables as required

# Boilerplate code to run the tests
if __name__ == '__main__':
    unittest.main()
