
# app.py
from flask import Flask, render_template, request, jsonify
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import base64
import io
import traceback
import json
from dijkstra1 import find_path_for_city

# Import your existing modules
from district_cities import DISTRICT_CITIES
from urgency_handler import get_city_urgency_scores

app = Flask(__name__)

# Define disaster types
DISASTER_TYPES = ['flood', 'landslide', 'avalanche', 'forestfire']

@app.route('/')
def index():
    return render_template(
        'index.html',
        districts=list(DISTRICT_CITIES.keys()),
        disasters=DISASTER_TYPES,
        district_cities=json.dumps(DISTRICT_CITIES)  # This is the key
    )



@app.route('/generate_heatmap', methods=['POST'])
def generate_heatmap():
    """Generate heatmap for selected district and disaster type"""
    try:
        data = request.get_json()
        district = data.get('district')
        disaster = data.get('disaster')
        use_live_weather = data.get('use_live_weather', False)
        
        if not district:
            return jsonify({'error': 'Please select a district first.'})
        
        if not disaster:
            return jsonify({'error': 'Please select a disaster type first.'})
        
        print(f"Selected district: {district}, disaster: {disaster}")  # Debug print
        print(f"Available districts: {list(DISTRICT_CITIES.keys())}")  # Debug print
        print("Calling get_city_urgency_scores...")  # Debug print
        
        # Validate district exists
        if district not in DISTRICT_CITIES:
            return jsonify({'error': f'District "{district}" not found in available districts.'})
        
        # Get urgency scores using your handler (pass disaster type)
        urgency_results = get_city_urgency_scores(district, DISTRICT_CITIES, disaster)
        
        # Debug print the results
        print(f"Urgency results: {urgency_results}")
        
        if not urgency_results:
            return jsonify({'error': f'No urgency data available for {disaster} in {district}.'})
        
        # Check if all results are None
        valid_results = {k: v for k, v in urgency_results.items() if v is not None}
        if not valid_results:
            return jsonify({'error': f'All urgency calculations failed for {disaster} in {district}. Check data files and API connectivity.'})
        
        # Generate plot
        plot_url = create_heatmap_plot(district, disaster, urgency_results)
        
        # Format city information
        city_info = format_city_info(urgency_results, disaster)
        
        return jsonify({
            'success': True,
            'plot_url': plot_url,
            'city_info': city_info,
            'status': f'Heatmap generated for {disaster} in {district}'
        })
        
    except Exception as e:
        error_msg = f"Error generating heatmap: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(error_msg)  # Print full error to console
        return jsonify({'error': error_msg})

def create_heatmap_plot(district, disaster, urgency_results):
    """Create matplotlib heatmap and return as base64 encoded image"""
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    import numpy as np

    # Setup figure and axis explicitly
    fig, ax = plt.subplots(figsize=(14, 8))

    # Extract city names and urgency scores, filtering out None values
    valid_data = [(city, score) for city, score in urgency_results.items() if score is not None]
    
    if not valid_data:
        # Create a placeholder plot if no valid data
        ax.text(0.5, 0.5, f'No valid urgency data for {disaster} in {district}', 
                ha='center', va='center', transform=ax.transAxes, fontsize=16)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title(f'{disaster.capitalize()} Urgency Heatmap - {district} (No Data)', 
                     fontsize=16, fontweight='bold')
    else:
        cities, scores = zip(*valid_data)
        
        # Normalize scores to 0-1 range for colormap
        scores_array = np.array(scores)
        normalized_scores = scores_array / max(scores_array) if max(scores_array) > 0 else scores_array
        
        # Create colormap
        colors = ['#2E8B57', '#32CD32', '#FFD700', '#FF8C00', '#FF4500', '#DC143C']  # Green to Red
        cmap = LinearSegmentedColormap.from_list('urgency', colors, N=256)
        
        # Create bar plot with disaster-specific colors
        bars = ax.bar(range(len(cities)), scores, color=cmap(normalized_scores))
        
        # Customize the plot
        ax.set_title(f'{disaster.capitalize()} Urgency Heatmap - {district}', 
                     fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel('Cities', fontsize=14, fontweight='bold')
        ax.set_ylabel('Urgency Score', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(cities)))
        ax.set_xticklabels(cities, rotation=45, ha='right', fontsize=10)
        ax.set_ylim(0, max(1.0, max(scores) * 1.1))
        
        # Add value labels on bars
        for i, (bar, score) in enumerate(zip(bars, scores)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{score:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Create ScalarMappable and attach colourbar to same figure and axis
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=1))
        sm.set_array([])  # Required for older versions
        cbar = fig.colorbar(sm, ax=ax, shrink=0.8)
        cbar.set_label('Urgency Level', rotation=270, labelpad=20, fontsize=12, fontweight='bold')
        
        # Add urgency level indicators on colorbar
        urgency_levels = ['Low', 'Medium', 'High', 'Critical']
        cbar.set_ticks([0.2, 0.4, 0.6, 0.8])
        cbar.set_ticklabels(urgency_levels)
        
        # Grid for better readability
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)

    fig.tight_layout()

    # Convert plot to base64
    img = io.BytesIO()
    fig.savefig(img, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)

    return plot_url

def format_city_info(urgency_results, disaster):
    """Format city information for display"""
    info_lines = []
    info_lines.append(f"=== {disaster.upper()} URGENCY SCORES ===\n")
    
    # Filter out None values and sort cities by urgency score (highest first)
    valid_results = {k: v for k, v in urgency_results.items() if v is not None}
    
    if not valid_results:
        info_lines.append("No valid urgency data available.")
        return "\n".join(info_lines)
    
    sorted_cities = sorted(valid_results.items(), key=lambda x: x[1], reverse=True)
    
    for i, (city, score) in enumerate(sorted_cities, 1):
        urgency_level = get_urgency_level(score)
        info_lines.append(f"{i}. {city}:")
        info_lines.append(f"   Score: {score:.3f}")
        info_lines.append(f"   Level: {urgency_level}")
        info_lines.append(f"   Disaster: {disaster.capitalize()}")
        info_lines.append("")
    
    # Add summary statistics
    scores = list(valid_results.values())
    info_lines.append("=== SUMMARY STATISTICS ===")
    info_lines.append(f"Total Cities Analyzed: {len(scores)}")
    info_lines.append(f"Average Urgency: {sum(scores)/len(scores):.3f}")
    info_lines.append(f"Highest Urgency: {max(scores):.3f}")
    info_lines.append(f"Lowest Urgency: {min(scores):.3f}")
    
    return "\n".join(info_lines)

def get_urgency_level(score):
    """Convert urgency score to descriptive level"""
    if score >= 0.8:
        return "🔴 CRITICAL"
    elif score >= 0.6:
        return "🟠 HIGH"
    elif score >= 0.4:
        return "🟡 MEDIUM"
    elif score >= 0.2:
        return "🟢 MODERATE"
    else:
        return "⚪ LOW"
    

@app.route('/find_path', methods=['POST'])
def find_path():
    data = request.get_json()
    city = data.get('city')

    if not city:
        return jsonify({'success': False, 'error': 'City name is required.'})

    result = find_path_for_city(city)

    if result.get('success'):
        return jsonify({
            'success': True,
            'city': result['city'],
            'relief_center': result['relief_center'],
            'distance_km': result['distance_km'],
            'map_file': result['map_file']
        })
    else:
        return jsonify({'success': False, 'error': result.get('error', 'Unknown error')})

@app.route('/get_cities', methods=['POST'])
def get_cities():
    data = request.get_json()
    district = data.get('district')
    
    if not district or district not in DISTRICT_CITIES:
        return jsonify({'success': False, 'error': 'Invalid district selected'})
    
    cities = [city[0] for city in DISTRICT_CITIES[district]]
    return jsonify({'success': True, 'cities': cities})


if __name__ == '__main__':
    print("Starting Flask Disaster Management App...")
    print(f"Available districts: {list(DISTRICT_CITIES.keys())}")
    print(f"Available disasters: {DISASTER_TYPES}")
    
    # Test the urgency calculation system
    print("\nTesting urgency calculation...")
    try:
        test_results = get_city_urgency_scores("Dehradun", DISTRICT_CITIES, "flood")
        print(f"Test results: {test_results}")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    app.run(debug=True, host='0.0.0.0', port=5000)