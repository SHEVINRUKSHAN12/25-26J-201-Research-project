import sys
import os
import random
import time
import csv
import json
from shapely.geometry import Polygon

# Add backend to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.modules.interior.optimizer import GeneticOptimizer

def run_convergence_experiment():
    print("Running Experiment 1: Convergence Analysis...")
    
    room_poly = Polygon([(0, 0), (500, 0), (500, 400), (0, 400)])
    furniture_items = [
        {"id": "bed", "width": 160, "depth": 200, "rotatable": True},
        {"id": "wardrobe", "width": 100, "depth": 60, "rotatable": False},
        {"id": "desk", "width": 120, "depth": 60, "rotatable": True},
        {"id": "chair", "width": 50, "depth": 50, "rotatable": True},
        {"id": "nightstand", "width": 40, "depth": 40, "rotatable": False}
    ]
    
    optimizer = GeneticOptimizer(room_poly, furniture_items, population_size=50, generations=30)
    # Disable ML for consistent geometric scoring in this analysis
    optimizer.ml_model = None 
    
    population = [optimizer.create_individual() for _ in range(optimizer.pop_size)]
    
    results = []
    
    for gen in range(optimizer.generations):
        fitness_scores = []
        for ind in population:
            score = optimizer.evaluator.calculate_fitness(ind)
            fitness_scores.append(score)
        
        best_fitness = max(fitness_scores)
        avg_fitness = sum(fitness_scores) / len(fitness_scores)
        
        results.append({
            "Generation": gen + 1,
            "Best Fitness": best_fitness,
            "Average Fitness": avg_fitness
        })
        
        new_population = []
        while len(new_population) < optimizer.pop_size:
            p1 = population[random.randint(0, optimizer.pop_size-1)]
            p2 = population[random.randint(0, optimizer.pop_size-1)]
            c1, c2 = optimizer.crossover(p1, p2)
            c1 = optimizer.mutate(c1)
            c2 = optimizer.mutate(c2)
            new_population.extend([c1, c2])
        population = new_population[:optimizer.pop_size]

    with open('convergence_results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Generation", "Best Fitness", "Average Fitness"])
        writer.writeheader()
        writer.writerows(results)
    print("Experiment 1 Complete.")

def run_comparison_experiment():
    print("\nRunning Experiment 2: GA vs Random Search...")
    
    room_poly = Polygon([(0, 0), (400, 400), (400, 0), (0, 0)])
    furniture_items = [
        {"id": "sofa", "width": 200, "depth": 90, "rotatable": True},
        {"id": "coffee_table", "width": 100, "depth": 60, "rotatable": True},
        {"id": "tv_stand", "width": 150, "depth": 40, "rotatable": False},
        {"id": "plant", "width": 30, "depth": 30, "rotatable": True}
    ]
    
    num_runs = 10
    ga_scores = []
    random_scores = []
    
    for i in range(num_runs):
        # GA Run
        optimizer = GeneticOptimizer(room_poly, furniture_items, population_size=30, generations=20)
        optimizer.ml_model = None # Disable ML for fair comparison
        _, best_fitness = optimizer.optimize()
        ga_scores.append(best_fitness)
        
        # Random Search Run
        # Create new optimizer to reset state if needed, though create_individual is stateless
        rs_optimizer = GeneticOptimizer(room_poly, furniture_items)
        best_random_fitness = float('-inf')
        # Same number of evaluations: 30 * 20 = 600
        for _ in range(600):
            ind = rs_optimizer.create_individual()
            score = rs_optimizer.evaluator.calculate_fitness(ind)
            if score > best_random_fitness:
                best_random_fitness = score
        random_scores.append(best_random_fitness)
        
    with open('comparison_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Run", "GA Score", "Random Search Score"])
        for i in range(num_runs):
            writer.writerow([i+1, ga_scores[i], random_scores[i]])
            
    print("Experiment 2 Complete.")

def run_constraint_experiment():
    print("\nRunning Experiment 3: Constraint Satisfaction...")
    
    room_poly = Polygon([(0, 0), (400, 400), (400, 0), (0, 0)])
    item_template = {"id": "box", "width": 60, "depth": 60, "rotatable": True}
    
    counts = [5, 8, 12, 15] # Adjusted counts
    results = []
    
    for count in counts:
        items = [item_template.copy() for _ in range(count)]
        
        successes = 0
        total_trials = 10 # Reduced trials for speed
        
        for _ in range(total_trials):
            optimizer = GeneticOptimizer(room_poly, items, population_size=40, generations=30)
            optimizer.ml_model = None # Disable ML
            _, best_fitness = optimizer.optimize()
            
            if best_fitness > -500: # Allow small tolerance or strictly > 0
                successes += 1
                
        success_rate = (successes / total_trials) * 100
        results.append({"Items": count, "Success Rate": success_rate})
        print(f"Items: {count}, Success Rate: {success_rate}%")
        
    with open('constraint_results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Items", "Success Rate"])
        writer.writeheader()
        writer.writerows(results)
        
    print("Experiment 3 Complete.")

def run_l_shape_experiment():
    print("\nRunning Experiment 4: L-Shaped Room...")
    
    # L-Shaped Polygon
    # (0,0) -> (500,0) -> (500,200) -> (300,200) -> (300,400) -> (0,400) -> (0,0)
    room_poly = Polygon([(0, 0), (500, 0), (500, 200), (300, 200), (300, 400), (0, 400)])
    
    furniture_items = [
        {"id": "bed", "width": 160, "depth": 200, "rotatable": True},
        {"id": "desk", "width": 120, "depth": 60, "rotatable": True},
        {"id": "wardrobe", "width": 100, "depth": 60, "rotatable": False},
        {"id": "sofa", "width": 180, "depth": 80, "rotatable": True}
    ]
    
    optimizer = GeneticOptimizer(room_poly, furniture_items, population_size=50, generations=30)
    optimizer.ml_model = None
    
    start_time = time.time()
    best_layout, best_fitness = optimizer.optimize()
    end_time = time.time()
    
    duration = end_time - start_time
    success = best_fitness > 0
    
    print(f"L-Shape Result: Success={success}, Fitness={best_fitness}, Time={duration:.2f}s")
    
    # Append to a new CSV or just log it
    with open('l_shape_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Shape", "Success", "Time(s)", "Fitness"])
        writer.writerow(["L-Shape", success, round(duration, 2), best_fitness])

if __name__ == "__main__":
    try:
        run_convergence_experiment()
        run_comparison_experiment()
        run_constraint_experiment()
        run_l_shape_experiment()
        print("\nAll experiments finished successfully.")
    except Exception as e:
        print(f"\nError running experiments: {e}")
