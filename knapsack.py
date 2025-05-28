# disaster_resource_allocator.py
import pandas as pd
from urgency_handler import get_city_urgency_scores
from district_cities import DISTRICT_CITIES

class DisasterResourceAllocator:
    """
    Emergency Resource Allocation System using Knapsack Algorithm
    
    This system solves the classic disaster management problem:
    "Given limited resources and budget, which cities should receive aid
    to maximize overall disaster relief effectiveness?"
    
    The Knapsack Algorithm is perfect for this because:
    - Each city is an "item" with a cost (resource cost) and value (relief effectiveness)
    - We have a limited "knapsack capacity" (total budget)
    - Goal: Maximize total relief value within budget constraints
    """
    
    def __init__(self):
        """Initialize with disaster-specific resource types and their characteristics"""
        self.disaster_resources = {
            'emergency_medical_team': {
                'cost': 50, 
                'effectiveness_multiplier': 1.0, 
                'description': 'Emergency Medical Response Team',
                'specialization': 'Critical for medical emergencies and casualties'
            },
            'search_rescue_team': {
                'cost': 40, 
                'effectiveness_multiplier': 0.8, 
                'description': 'Search and Rescue Team',
                'specialization': 'Specialized for trapped victims and evacuations'
            },
            'relief_supplies': {
                'cost': 20, 
                'effectiveness_multiplier': 0.6, 
                'description': 'Emergency Relief Supplies',
                'specialization': 'Food, water, shelter materials for displaced populations'
            },
            'heavy_equipment': {
                'cost': 30, 
                'effectiveness_multiplier': 0.7, 
                'description': 'Heavy Rescue Equipment',
                'specialization': 'Machinery for debris removal and infrastructure repair'
            },
            'evacuation_transport': {
                'cost': 35, 
                'effectiveness_multiplier': 0.75, 
                'description': 'Emergency Transportation',
                'specialization': 'Vehicles and logistics for mass evacuations'
            }
        }
    
    def knapsack_dp(self, cities_data, total_budget):
        """
        KNAPSACK ALGORITHM - MANUAL IMPLEMENTATION
        
        Classic Dynamic Programming solution for 0/1 Knapsack Problem
        Applied to disaster resource allocation:
        
        Problem: Given N cities needing aid and a budget B, select cities to maximize relief value
        - Each city has: cost (resource deployment cost) and value (expected relief impact)
        - Constraint: Total cost ≤ Budget
        - Objective: Maximize total relief value
        
        Time Complexity: O(N × Budget)
        Space Complexity: O(N × Budget)
        """
        n = len(cities_data)
        if n == 0 or total_budget <= 0:
            return []
        
        # DP table: dp[i][w] = max relief value using first i cities with budget w
        dp = [[0 for _ in range(total_budget + 1)] for _ in range(n + 1)]
        
        # Fill DP table using recurrence relation
        for i in range(1, n + 1):
            city_name, disaster_urgency, resource_cost, relief_value = cities_data[i-1]
            
            for budget_remaining in range(total_budget + 1):
                # Option 1: Don't deploy resources to this city
                dp[i][budget_remaining] = dp[i-1][budget_remaining]
                
                # Option 2: Deploy resources to this city (if budget allows)
                if resource_cost <= budget_remaining:
                    include_city_value = dp[i-1][budget_remaining - resource_cost] + relief_value
                    # Take maximum of both options
                    dp[i][budget_remaining] = max(dp[i][budget_remaining], include_city_value)
        
        # Backtrack to find which cities were selected for optimal solution
        selected_cities = []
        remaining_budget = total_budget
        
        for i in range(n, 0, -1):
            # If value changed, this city was included in optimal solution
            if dp[i][remaining_budget] != dp[i-1][remaining_budget]:
                city_name, disaster_urgency, resource_cost, relief_value = cities_data[i-1]
                selected_cities.append({
                    'city': city_name,
                    'disaster_urgency': disaster_urgency,
                    'deployment_cost': resource_cost,
                    'relief_value': relief_value,
                    'efficiency_ratio': relief_value / resource_cost
                })
                remaining_budget -= resource_cost
        
        # Return in deployment priority order (highest urgency first)
        return sorted(selected_cities, key=lambda x: x['disaster_urgency'], reverse=True)
    
    def calculate_relief_value(self, disaster_urgency, resource_type):
        """
        Calculate expected relief value from deploying resources to a city
        
        Relief Value = Disaster Urgency × Base Scale × Resource Effectiveness
        - Higher urgency cities get proportionally more value
        - Different resources have different effectiveness multipliers
        """
        base_relief_scale = 100  # Scale urgency score (0-1) to relief value (0-100)
        resource_effectiveness = self.disaster_resources[resource_type]['effectiveness_multiplier']
        
        return disaster_urgency * base_relief_scale * resource_effectiveness
    
    def prepare_disaster_data(self, district, resource_type='emergency_medical_team'):
        """
        Transform city urgency data into knapsack problem format
        
        Each city becomes a knapsack "item" with:
        - Weight = Resource deployment cost
        - Value = Expected disaster relief effectiveness
        """
        if district not in DISTRICT_CITIES:
            raise ValueError(f"District '{district}' not found in emergency database!")
        
        # Extract city names from coordinate tuples
        district_cities = {district: [city_info[0] for city_info in DISTRICT_CITIES[district]]}
        
        # Get real-time disaster urgency scores
        urgency_scores = get_city_urgency_scores(district, district_cities)
        
        # Filter cities with valid urgency data
        affected_cities = {city: urgency for city, urgency in urgency_scores.items() 
                          if urgency is not None and urgency > 0}
        
        if not affected_cities:
            raise ValueError(f"No cities with disaster urgency found in district: {district}")
        
        # Convert to knapsack format: (city, urgency, cost, relief_value)
        knapsack_data = []
        resource_cost = self.disaster_resources[resource_type]['cost']
        
        for city, urgency_score in affected_cities.items():
            relief_value = self.calculate_relief_value(urgency_score, resource_type)
            knapsack_data.append((city, urgency_score, resource_cost, relief_value))
        
        # Sort by urgency (critical cities first) for better algorithm performance
        return sorted(knapsack_data, key=lambda x: x[1], reverse=True)
    
    def deploy_disaster_resources(self, district, emergency_budget, resource_type='emergency_medical_team'):
        """
        MAIN DISASTER RESPONSE FUNCTION
        
        Uses Knapsack Algorithm to optimally allocate disaster relief resources
        """
        print(f"\n{'='*70}")
        print(f"🚨 EMERGENCY RESOURCE DEPLOYMENT - DISTRICT: {district.upper()}")
        print(f"{'='*70}")
        
        resource_info = self.disaster_resources[resource_type]
        print(f"📦 Resource Type: {resource_info['description']}")
        print(f"💰 Available Budget: ${emergency_budget:,}")
        print(f"💵 Cost per Deployment: ${resource_info['cost']}")
        print(f"🎯 Specialization: {resource_info['specialization']}")
        print(f"📊 Effectiveness Rating: {resource_info['effectiveness_multiplier']:.1%}")
        print("-" * 70)
        
        try:
            # Prepare disaster data for knapsack algorithm
            disaster_data = self.prepare_disaster_data(district, resource_type)
            
            print(f"🏙️  DISASTER ASSESSMENT - {len(disaster_data)} cities require aid:")
            print(f"{'City':<20} {'Urgency':<10} {'Relief Value':<12} {'Efficiency':<10}")
            print("-" * 55)
            
            for city, urgency, cost, value in disaster_data:
                efficiency = value / cost
                urgency_level = "🔴 CRITICAL" if urgency > 0.7 else "🟡 HIGH" if urgency > 0.4 else "🟢 MODERATE"
                print(f"{city:<20} {urgency_level:<10} {value:<12.1f} {efficiency:<10.2f}")
            
            # Apply Knapsack Algorithm for optimal resource allocation
            print(f"\n🧮 APPLYING KNAPSACK ALGORITHM...")
            print(f"   → Evaluating {len(disaster_data)} cities with budget ${emergency_budget:,}")
            print(f"   → Finding optimal combination to maximize disaster relief...")
            
            optimal_deployment = self.knapsack_dp(disaster_data, emergency_budget)
            
            if not optimal_deployment:
                print("\n❌ DEPLOYMENT FAILED: Insufficient budget for any resource deployment")
                return None
            
            # Calculate deployment statistics
            total_deployment_cost = sum(city['deployment_cost'] for city in optimal_deployment)
            total_relief_value = sum(city['relief_value'] for city in optimal_deployment)
            cities_helped = len(optimal_deployment)
            cities_total = len(disaster_data)
            budget_efficiency = (total_relief_value / total_deployment_cost) * 100
            
            print(f"\n{'='*70}")
            print(f"✅ OPTIMAL DEPLOYMENT PLAN - KNAPSACK SOLUTION")
            print(f"{'='*70}")
            print(f"🏥 Cities to Receive Aid: {cities_helped}/{cities_total}")
            print(f"💰 Total Deployment Cost: ${total_deployment_cost:,}")
            print(f"📈 Total Relief Value: {total_relief_value:.1f}")
            print(f"💡 Budget Efficiency: {budget_efficiency:.1f} relief points per $100")
            print(f"💵 Remaining Budget: ${emergency_budget - total_deployment_cost:,}")
            
            print(f"\n🎯 DEPLOYMENT PRIORITY ORDER:")
            print(f"{'Rank':<6} {'City':<20} {'Urgency':<10} {'Relief Value':<12} {'Status':<15}")
            print("-" * 70)
            
            for rank, city_info in enumerate(optimal_deployment, 1):
                urgency = city_info['disaster_urgency']
                status = "🔴 CRITICAL" if urgency > 0.7 else "🟡 HIGH PRIORITY" if urgency > 0.4 else "🟢 STANDARD"
                
                print(f"{rank:<6} {city_info['city']:<20} "
                      f"{urgency:<10.3f} {city_info['relief_value']:<12.1f} {status:<15}")
            
            return optimal_deployment
            
        except ValueError as e:
            print(f"❌ ERROR: {e}")
            return None
        except Exception as e:
            print(f"❌ SYSTEM ERROR: {e}")
            return None
    
    def compare_resource_strategies(self, district, emergency_budget):
        """
        Compare effectiveness of different disaster response strategies
        Demonstrates how knapsack algorithm helps choose optimal resource types
        """
        print(f"\n{'='*80}")
        print(f"📊 DISASTER RESPONSE STRATEGY COMPARISON - {district.upper()}")
        print(f"📍 Emergency Budget: ${emergency_budget:,}")
        print(f"{'='*80}")
        
        strategy_results = {}
        
        print("🔄 Analyzing each resource type with Knapsack Algorithm...\n")
        
        for resource_type, resource_info in self.disaster_resources.items():
            try:
                disaster_data = self.prepare_disaster_data(district, resource_type)
                optimal_deployment = self.knapsack_dp(disaster_data, emergency_budget)
                
                if optimal_deployment:
                    cities_count = len(optimal_deployment)
                    total_cost = sum(city['deployment_cost'] for city in optimal_deployment)
                    total_value = sum(city['relief_value'] for city in optimal_deployment)
                    efficiency = (total_value / total_cost) if total_cost > 0 else 0
                    coverage = (cities_count / len(disaster_data)) * 100
                    
                    strategy_results[resource_type] = {
                        'cities_helped': cities_count,
                        'total_cost': total_cost,
                        'relief_value': total_value,
                        'efficiency': efficiency,
                        'coverage_percent': coverage,
                        'description': resource_info['description']
                    }
                    
            except Exception as e:
                print(f"⚠️  Unable to analyze {resource_type}: {e}")
        
        if not strategy_results:
            print("❌ No viable strategies found for current budget")
            return None
        
        # Display comparison table
        print(f"📈 KNAPSACK OPTIMIZATION RESULTS:")
        print(f"{'Strategy':<25} {'Cities':<8} {'Cost':<10} {'Relief':<10} {'Efficiency':<12} {'Coverage':<10}")
        print("-" * 85)
        
        # Sort by efficiency (best strategy first)
        sorted_strategies = sorted(strategy_results.items(), key=lambda x: x[1]['efficiency'], reverse=True)
        
        for resource_type, results in sorted_strategies:
            print(f"{resource_type:<25} "
                  f"{results['cities_helped']:<8} "
                  f"${results['total_cost']:<9,} "
                  f"{results['relief_value']:<10.0f} "
                  f"{results['efficiency']:<12.1f} "
                  f"{results['coverage_percent']:<10.1f}%")
        
        # Highlight best strategy
        best_strategy = sorted_strategies[0]
        print(f"\n🏆 RECOMMENDED STRATEGY: {best_strategy[0].upper()}")
        print(f"   📋 {best_strategy[1]['description']}")
        print(f"   🎯 Highest efficiency: {best_strategy[1]['efficiency']:.1f} relief points per dollar")
        print(f"   🏙️  Will help {best_strategy[1]['cities_helped']} cities")
        
        return strategy_results

def main():
    """
    Disaster Management Command Center
    Demonstrates practical application of Knapsack Algorithm in emergency response
    """
    print("🚨" * 25)
    print("    DISASTER RESOURCE ALLOCATION SYSTEM")
    print("      Powered by Knapsack Algorithm")
    print("🚨" * 25)
    
    print("\n📝 PROBLEM CONTEXT:")
    print("When disasters strike, emergency resources are limited but cities need immediate aid.")
    print("The Knapsack Algorithm helps us optimally allocate resources to maximize lives saved.")
    print("\n🧮 HOW KNAPSACK APPLIES:")
    print("• Each city = an 'item' with deployment cost and relief value")
    print("• Emergency budget = 'knapsack capacity'")
    print("• Goal = maximize total relief value within budget constraints")
    
    allocator = DisasterResourceAllocator()
    
    # Get disaster scenario input
    print(f"\n{'='*50}")
    district = input("🏢 Enter affected district: ").strip()
    
    try:
        budget = int(input("💰 Enter emergency budget: $"))
        if budget <= 0:
            print("❌ Budget must be positive!")
            return
    except ValueError:
        print("❌ Invalid budget amount!")
        return
    
    # Validate district
    if district not in DISTRICT_CITIES:
        print(f"❌ District '{district}' not in emergency database!")
        print(f"📍 Available districts: {list(DISTRICT_CITIES.keys())}")
        return
    
    # Show available resources
    print(f"\n🚑 AVAILABLE EMERGENCY RESOURCES:")
    for i, (resource_type, info) in enumerate(allocator.disaster_resources.items(), 1):
        print(f"{i}. {info['description']} - ${info['cost']} per deployment")
        print(f"   🎯 {info['specialization']}")
    
    # Get resource selection
    try:
        choice = input(f"\n📦 Select resource type (1-{len(allocator.disaster_resources)} or name): ").strip()
        resource_types_list = list(allocator.disaster_resources.keys())
        
        if choice.isdigit() and 1 <= int(choice) <= len(resource_types_list):
            selected_resource = resource_types_list[int(choice) - 1]
        elif choice in allocator.disaster_resources:
            selected_resource = choice
        else:
            selected_resource = 'emergency_medical_team'  # Default to most critical
            print(f"⚠️  Using default: Emergency Medical Team")
            
    except (IndexError, ValueError):
        selected_resource = 'emergency_medical_team'
        print(f"⚠️  Using default: Emergency Medical Team")
    
    # Execute optimal deployment using Knapsack Algorithm
    deployment_plan = allocator.deploy_disaster_resources(district, budget, selected_resource)
    
    # Offer strategy comparison
    if deployment_plan:
        compare_input = input(f"\n🔄 Compare all resource strategies? (y/n): ").strip().lower()
        if compare_input in ['y', 'yes']:
            allocator.compare_resource_strategies(district, budget)
            
        print(f"\n✅ Disaster response plan generated using Knapsack optimization!")
        print(f"📊 This algorithm ensures maximum relief impact within budget constraints.")

if __name__ == "__main__":
    main()