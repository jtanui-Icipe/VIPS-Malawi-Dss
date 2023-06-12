import datetime, pytz
import unittest
import logging
from src.vips_malawi_dss_model.malawi_dss_model import *
import vipscore_common.data_utils

def get_temperature_data():
    with open("tests/tm.json") as f:
        return get_weather_observations_from_json(f.read())

def get_lw_data():
    with open("tests/bt.json") as f:
        return get_weather_observations_from_json(f.read())

class TestMalawiDssModel(unittest.TestCase):
    def test_get_date_when_day_degree_limit_has_passed(self):
        # Get observations list
        observations = get_temperature_data()
        # Instantiate the model
        instance = MalawiDssModel()
        result = instance.get_date_when_day_degree_limit_has_passed(observations)
        expected_date = datetime(2016, 5, 25, 22, 0, tzinfo=pytz.timezone("UTC"))
        self.assertEquals(result, expected_date)

    def test_get_infection_risk(self):
        # Get observations list
        observations = get_lw_data()
        instance = MalawiDssModel()
        result = instance.get_infection_risk(observations)
        self.assertIsNotNone(result)

    def test_get_result(self):
        """
        We get an infection risk of 10 at a certain point in the time series
        """
        tm_obs = get_temperature_data()
        lw_obs = get_lw_data()

        observations = tm_obs + lw_obs

        instance = MalawiDssModel()
        model_config = ModelConfiguration(
            model_id=instance.MODEL_ID,
            config_parameters={"observations": observations}
        )
        instance.set_configuration(model_config)

        results = instance.get_result()

        self.assertIsNotNone(results)

        self.assertEqual(int(results[5094].get_value(instance.MODEL_ID, instance.CONTROLLED_INFECTION_RISK)), 10)
