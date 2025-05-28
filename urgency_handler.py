
'''# urgency_handler.py
import pandas as pd
from urgency_score import urgency
from weather import get_weather_code

# Load all data once
population_df = pd.read_csv("population.csv", index_col="City")
severity_df = pd.read_csv("severity.csv", index_col="City") 
deaths_df = pd.read_csv("deaths.csv", index_col="City")

def get_city_urgency_scores(district, district_cities):
    results = {}
    for city in district_cities[district]:
        try:
            pop = population_df.loc[city].iloc[0] if hasattr(population_df.loc[city], 'iloc') else population_df.loc[city]
            sev = severity_df.loc[city].iloc[0] if hasattr(severity_df.loc[city], 'iloc') else severity_df.loc[city]
            deaths = deaths_df.loc[city].iloc[0] if hasattr(deaths_df.loc[city], 'iloc') else deaths_df.loc[city]
            weather = get_weather_code(city)
            
            # Handle case where weather API returns -1 (error)
            if weather == -1:
                weather = 1.5  # Use default moderate weather value
            
            # Fix parameter name - use 'weather' not 'weather_index'
            urgency_score = urgency(
                deaths=deaths,
                severity=sev, 
                weather=weather,
                population=pop
            )
            results[city] = urgency_score
        except Exception as e:
            print(f"Error processing {city}: {e}")
            results[city] = None
    return results'''
    
'''# urgency_handler.py
import pandas as pd
from urgency_score import urgency
from weather import get_weather_code

# Load all data once
population_df = pd.read_csv("population.csv", index_col="City")
severity_df = pd.read_csv("severity.csv", index_col="City") 
deaths_df = pd.read_csv("deaths.csv", index_col="City")

def get_city_urgency_scores(district, district_cities, disaster_type=None):
    """
    Get urgency scores for cities in a district, optionally filtered by disaster type
    
    Args:
        district: Name of the district
        district_cities: Dict mapping districts to cities
        disaster_type: Type of disaster (flood, landslide, avalanche, forestfire)
    """
    results = {}
    
    # Disaster multipliers to adjust urgency based on disaster type
    disaster_multipliers = {
        'flood': 1.2,
        'landslide': 1.1,
        'avalanche': 1.0,
        'forestfire': 1.15
    }
    
    disaster_multiplier = disaster_multipliers.get(disaster_type, 1.0) if disaster_type else 1.0
    
    for city in district_cities[district]:
        try:
            pop = population_df.loc[city].iloc[0] if hasattr(population_df.loc[city], 'iloc') else population_df.loc[city]
            sev = severity_df.loc[city].iloc[0] if hasattr(severity_df.loc[city], 'iloc') else severity_df.loc[city]
            deaths = deaths_df.loc[city].iloc[0] if hasattr(deaths_df.loc[city], 'iloc') else deaths_df.loc[city]
            weather = get_weather_code(city)
            
            # Handle case where weather API returns -1 (error)
            if weather == -1:
                weather = 1.5  # Use default moderate weather value
            
            # Adjust weather based on disaster type
            if disaster_type:
                weather = adjust_weather_for_disaster(weather, disaster_type)
            
            # Calculate base urgency score
            urgency_score = urgency(
                deaths=deaths,
                severity=sev, 
                weather=weather,
                population=pop
            )
            
            # Apply disaster-specific multiplier
            final_score = min(urgency_score * disaster_multiplier, 1.0)
            results[city] = final_score
            
        except Exception as e:
            print(f"Error processing {city}: {e}")
            results[city] = None
    
    return results

def adjust_weather_for_disaster(weather_code, disaster_type):
    """
    Adjust weather impact based on disaster type
    
    Args:
        weather_code: Current weather code
        disaster_type: Type of disaster
    
    Returns:
        Adjusted weather impact value
    """
    # Base weather impact adjustments for different disasters
    disaster_weather_impact = {
        'flood': {
            'heavy_rain': 2.5,  # High impact
            'moderate_rain': 2.0,
            'light_rain': 1.5,
            'clear': 1.0
        },
        'landslide': {
            'heavy_rain': 2.8,  # Very high impact
            'moderate_rain': 2.2,
            'light_rain': 1.8,
            'clear': 1.0
        },
        'avalanche': {
            'heavy_snow': 2.7,
            'moderate_snow': 2.0,
            'light_snow': 1.5,
            'clear': 1.0
        },
        'forestfire': {
            'hot_dry': 2.6,
            'windy': 2.3,
            'moderate': 1.5,
            'humid': 0.8  # Lower risk
        }
    }
    
    # Simple mapping - you can make this more sophisticated based on actual weather codes
    if disaster_type in disaster_weather_impact:
        # For now, use weather_code as is and apply basic multiplier
        if weather_code >= 2.5:  # Severe weather
            return min(weather_code * 1.2, 3.0)
        elif weather_code >= 2.0:  # Moderate weather
            return weather_code * 1.1
        else:  # Mild weather
            return weather_code
    
    return weather_code'''

import pandas as pd
from urgency_score import urgency
from weather import get_weather_code

# Load all data once
try:
    population_df = pd.read_csv("population.csv", index_col="City")
    severity_df = pd.read_csv("severity.csv", index_col="City") 
    deaths_df = pd.read_csv("deaths.csv", index_col="City")
    print("Data files loaded successfully")
except Exception as e:
    print(f"Error loading data files: {e}")

def get_city_urgency_scores(district, district_cities, disaster_type=None):
    """
    Get urgency scores for cities in a district, optionally filtered by disaster type
    
    Args:
        district: Name of the district
        district_cities: Dict mapping districts to cities
        disaster_type: Type of disaster (flood, landslide, avalanche, forestfire)
    """
    results = {}
    
    print(f"Processing district: {district}")
    print(f"Disaster type: {disaster_type}")
    
    if district not in district_cities:
        print(f"District {district} not found in district_cities")
        return results
    
    # Disaster multipliers to adjust urgency based on disaster type
    disaster_multipliers = {
        'flood': 1.2,
        'landslide': 1.1,
        'avalanche': 1.0,
        'forestfire': 1.15
    }
    
    disaster_multiplier = disaster_multipliers.get(disaster_type, 1.0) if disaster_type else 1.0
    print(f"Using disaster multiplier: {disaster_multiplier}")
    
    # Map disaster types to CSV column names
    disaster_column_mapping = {
        'flood': 'Flood',
        'landslide': 'Landslide', 
        'avalanche': 'Avalanche',
        'forestfire': 'Forest Fire'  # Note: CSV uses 'Forest Fire'
    }
    
    # Get the cities for this district (extract city names from tuples)
    cities_in_district = []
    for city_info in district_cities[district]:
        if isinstance(city_info, tuple):
            city_name = city_info[0]  # Extract city name from tuple
        else:
            city_name = city_info  # In case it's just a string
        cities_in_district.append(city_name)
    
    print(f"Cities to process: {cities_in_district}")
    
    for city in cities_in_district:
        try:
            print(f"\nProcessing city: {city}")
            
            # Get population (normalized)
            if city in population_df.index:
                pop = population_df.loc[city, 'Normalized_Population']
                print(f"Population: {pop}")
            else:
                print(f"Population data not found for {city}")
                pop = 5.0  # Default value
            
            # Get severity based on disaster type
            if city in severity_df.index and disaster_type:
                disaster_col = disaster_column_mapping.get(disaster_type, 'Flood')
                if disaster_col in severity_df.columns:
                    sev = severity_df.loc[city, disaster_col]
                    print(f"Severity ({disaster_col}): {sev}")
                else:
                    print(f"Severity column {disaster_col} not found")
                    sev = 5.0  # Default
            else:
                print(f"Severity data not found for {city}")
                sev = 5.0  # Default
            
            # Get deaths based on disaster type  
            if city in deaths_df.index and disaster_type:
                disaster_col = disaster_column_mapping.get(disaster_type, 'Flood')
                if disaster_col in deaths_df.columns:
                    deaths = deaths_df.loc[city, disaster_col]
                    print(f"Deaths ({disaster_col}): {deaths}")
                else:
                    print(f"Deaths column {disaster_col} not found")
                    deaths = 5  # Default
            else:
                print(f"Deaths data not found for {city}")
                deaths = 5  # Default
            
            # Get weather data
            weather = get_weather_code(city)
            print(f"Weather code: {weather}")
            
            # Handle case where weather API returns -1 (error)
            if weather == -1:
                weather = 1.5  # Use default moderate weather value
                print(f"Using default weather: {weather}")
            
            # Adjust weather based on disaster type
            if disaster_type:
                weather = adjust_weather_for_disaster(weather, disaster_type)
                print(f"Adjusted weather: {weather}")
            
            # Calculate base urgency score
            urgency_score = urgency(
                deaths=deaths,
                severity=sev, 
                weather=weather,
                population=pop
            )
            print(f"Base urgency score: {urgency_score}")
            
            # Apply disaster-specific multiplier
            final_score = min(urgency_score * disaster_multiplier, 1.0)
            print(f"Final urgency score: {final_score}")
            
            results[city] = final_score
            
        except Exception as e:
            print(f"Error processing {city}: {e}")
            import traceback
            traceback.print_exc()
            results[city] = None
    
    print(f"\nFinal results: {results}")
    return results

def adjust_weather_for_disaster(weather_code, disaster_type):
    """
    Adjust weather impact based on disaster type
    
    Args:
        weather_code: Current weather code
        disaster_type: Type of disaster
    
    Returns:
        Adjusted weather impact value
    """
    # Base weather impact adjustments for different disasters
    disaster_weather_impact = {
        'flood': {
            'heavy_rain': 2.5,  # High impact
            'moderate_rain': 2.0,
            'light_rain': 1.5,
            'clear': 1.0
        },
        'landslide': {
            'heavy_rain': 2.8,  # Very high impact
            'moderate_rain': 2.2,
            'light_rain': 1.8,
            'clear': 1.0
        },
        'avalanche': {
            'heavy_snow': 2.7,
            'moderate_snow': 2.0,
            'light_snow': 1.5,
            'clear': 1.0
        },
        'forestfire': {
            'hot_dry': 2.6,
            'windy': 2.3,
            'moderate': 1.5,
            'humid': 0.8  # Lower risk
        }
    }
    
    # Simple mapping - you can make this more sophisticated based on actual weather codes
    if disaster_type in disaster_weather_impact:
        # For now, use weather_code as is and apply basic multiplier
        if weather_code >= 2.5:  # Severe weather
            return min(weather_code * 1.2, 3.0)
        elif weather_code >= 2.0:  # Moderate weather
            return weather_code * 1.1
        else:  # Mild weather
            return weather_code
    
    return weather_code

# Test function
if __name__ == "__main__":
    from district_cities import DISTRICT_CITIES
    
    # Test with a sample district and disaster
    test_district = "Dehradun"
    test_disaster = "flood"
    
    print(f"Testing with district: {test_district}, disaster: {test_disaster}")
    results = get_city_urgency_scores(test_district, DISTRICT_CITIES, test_disaster)
    print(f"Test results: {results}")