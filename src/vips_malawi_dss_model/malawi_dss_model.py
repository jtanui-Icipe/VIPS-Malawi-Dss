from vipscore_common.vips_model import VIPSModel
from vipscore_common.entities import Result, ModelConfiguration, WeatherObservation, WeatherElements
from vipscore_common.data_utils import *


class MalawiDssModel(VIPSModel):
    """
        This is the result of a VIPS Model implementation class
    """

    MODEL_ID = "FUNGUSPILO"
    COPYRIGHT = "(c) 2023 ACME Industries"

    THRESHOLD = 500.0
    observations = None
    CONTROLLED_INFECTION_RISK = "CONTROLLED_INFECTION_RISK"

    def get_date_when_day_degree_limit_has_passed(self, observations: list):
        # Initalize the day degree counter
        day_degrees = 0.0
        # Iterate through the list of observations
        # !! Assuming the observations list is sorted chronologically!!
        for observation in observations:
            # Make sure it's only daily temperature observations that are used
            if observation.logIntervalId == WeatherObservation.LOG_INTERVAL_ID_1D and observation.elementMeasurementTypeId == WeatherElements.TEMPERATURE_MEAN:
                # Add to day_degree_sum
                day_degrees = day_degrees + observation.value
                # If threshold is reached, return the date of the current temperature measurement
                if day_degrees >= self.THRESHOLD:
                    return observation.timeMeasured
        # We have finished looping through the observations, and dayDegrees has
        # not passed 500. So we can't return a Date, we must return None(nothing)
        return None

    def get_infection_risk(self, observations: list):
        # Create the map with dates and infection risk values
        risk_map = {}

        # Counter for consecutive hours of leaf wetness
        consecutive_hours_with_leaf_wetness = 0

        # !! Assuming the observations list is sorted chronologically!!
        # Loop through the list of observations
        for observation in observations:
            # We define a lower threshold for leaf wetnes to be 10mins/hour
            if observation.value > 10.0:
                # Leaf wetness registered, add to consecutive hours counter
                consecutive_hours_with_leaf_wetness = consecutive_hours_with_leaf_wetness + 1
            else:
                # No leaf wetness, reset counter
                consecutive_hours_with_leaf_wetness = 0
            # We set the risk value
            risk_map[observation.timeMeasured] = consecutive_hours_with_leaf_wetness * 2
        # Return the map with all values
        return risk_map

    def set_configuration(self, model_configuration: ModelConfiguration):
        """
            Set the configuration object (with all its possible parameters)
            Must be done before you call get_result
        """
        # Get the observation list, using the data_utils helper module
        self.observations = get_weather_observations_from_json_list(
            model_configuration.config_parameters["observations"])

    def get_result(self) -> list[Result]:
        """Get the results as a list of Result objects (TODO ref)"""
        # Initialize the list of results
        results = []
        # !! Assuming the observations list is sorted chronologically!! TODO Sort algorithm
        # Which date did day degree sum exceed 500?
        day_degree_limit_reach_date = self.get_date_when_day_degree_limit_has_passed(self.observations)

        # Get infection risk for the whole period
        uncontrolled_infection_risk = self.get_infection_risk(self.observations)
        # Get all dates from the map of infection risk
        date_list = list(uncontrolled_infection_risk.keys())
        date_list.sort()

        for current_date in date_list:
            result = Result(
                validTimeStart=current_date,
                validTimeEnd=None,
                warningStatus=0 # Temporary, set it later
            )

            # If we're after the date of day degree sum > 500, use the infectionrisk
            if current_date >= day_degree_limit_reach_date:
                # Set infection risk
                result.set_value(self.MODEL_ID, self.CONTROLLED_INFECTION_RISK, "%s" % uncontrolled_infection_risk[current_date])
            else:
                # Set infection risk to 0
                result.set_value(self.MODEL_ID, self.CONTROLLED_INFECTION_RISK, "0")

            # Set the warning status
            # If controlled infection risk < 64, status is NO RISK
            # Otherwise it's HIGH RISK
            result.warning_status = Result.WARNING_STATUS_NO_RISK if uncontrolled_infection_risk[current_date] <64 else Result.WARNING_STATUS_HIGH_RISK
            results.append(result)
        return results

    @property
    def model_id(self) -> str:
        """10-character ID of the model. Must be unique (at least in the current system)"""
        pass

    @property
    def sample_config(self) -> dict:
        """A sample configuration in JSON format (TODO check relation with Dict)"""
        pass

    @property
    def license(self) -> str:
        """Returns the license for this piece of software"""
        pass

    @property
    def copyright(self) -> str:
        """Name of person/organization that holds the copyright, and contact information"""
        pass

    def get_model_name(self, language: str) -> str:
        """Returns the model name in the specified language (<a href="http://www.loc.gov/standards/iso639-2/php/English_list.php">ISO-639-2</a>)"""
        pass

    def get_model_description(self, language: str) -> str:
        """Returns the model description in the specified language (<a href="http://www.loc.gov/standards/iso639-2/php/English_list.php">ISO-639-2</a>)"""
        pass

    def get_warning_status_interpretation(self, language: str) -> str:
        """How to interpret the warning status (red-yellow-green, what does it mean?) in the specified language (<a href="http://www.loc.gov/standards/iso639-2/php/English_list.php">ISO-639-2</a>)"""
        pass

    def get_model_usage(self, language: str) -> str:
        """Technical manual for this model, in the specified language  (<a href="http://www.loc.gov/standards/iso639-2/php/English_list.php">ISO-639-2</a>)"""
        pass

