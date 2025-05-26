RELIEF_CENTRES = {
    "Dehradun": {
        "District Disaster Management Authority (DDMA) - Dehradun": (30.3165, 78.0322),
        "State Disaster Response Force (SDRF) Headquarters - Dehradun": (30.3255, 78.0367),
        "State Emergency Operations Center - Dehradun": (30.3190, 78.0281)
    },
    
    "Haridwar": {
        "District Disaster Management Authority (DDMA) - Haridwar": (29.9457, 78.1642),
        "SDRF Regional Unit - Haridwar": (29.9520, 78.1680),
        "Red Cross District Center - Haridwar": (29.9380, 78.1590)
    },
    
    "Nainital": {
        "District Disaster Management Authority (DDMA) - Nainital": (29.3919, 79.4542),
        "SDRF Hill Region Unit - Nainital": (29.3980, 79.4600),
        "Tourist Emergency Response Center - Nainital": (29.3850, 79.4480)
    },
    
    "Chamoli": {
        "District Disaster Management Authority (DDMA) - Chamoli (Gopeshwar)": (30.4067, 79.3289),
        "High Altitude Rescue Center - Joshimath": (30.5563, 79.5639),
        "Badrinath Route Emergency Center - Chamoli": (30.4100, 79.3350)
    },
    
    "Uttarkashi": {
        "District Disaster Management Authority (DDMA) - Uttarkashi": (30.7268, 78.4354),
        "Gangotri Route Relief Center - Uttarkashi": (30.7320, 78.4400),
        "ITBP Emergency Response Unit - Uttarkashi": (30.7200, 78.4300)
    },
    
    "Pithoragarh": {
        "District Disaster Management Authority (DDMA) - Pithoragarh": (29.5831, 80.2167),
        "Border Area Relief Center - Pithoragarh": (29.5900, 80.2200),
        "ITBP Disaster Response Unit - Pithoragarh": (29.5780, 80.2120)
    },
    
    "Almora": {
        "District Disaster Management Authority (DDMA) - Almora": (29.5971, 79.6593)
    },
    
    "Rudraprayag": {
        "District Disaster Management Authority (DDMA) - Rudraprayag": (30.2839, 78.9811)
    },
    
    "Bageshwar": {
        "District Disaster Management Authority (DDMA) - Bageshwar": (29.8372, 79.7683)
    },
    
    "Champawat": {
        "District Disaster Management Authority (DDMA) - Champawat": (29.3367, 80.0933)
    },
    
    "Pauri Garhwal": {
        "District Disaster Management Authority (DDMA) - Pauri": (30.1486, 78.7814)
    },
    
    "Tehri Garhwal": {
        "District Disaster Management Authority (DDMA) - New Tehri": (30.3889, 78.4811)
    },
    
    "Udham Singh Nagar": {
        "District Disaster Management Authority (DDMA) - Rudrapur": (28.9845, 79.4079)
    }
}

'''# Example of how to access the data:
# Print all relief centers in Dehradun district
print("Relief Centers in Dehradun:")
for center, coordinates in uttarakhand_relief_centers["Dehradun"].items():
    print(f"- {center}: {coordinates}")

# Print all districts with multiple relief centers
print("\nDistricts with multiple relief centers:")
for district, centers in uttarakhand_relief_centers.items():
    if len(centers) > 1:
        print(f"- {district}: {len(centers)} centers")'''
