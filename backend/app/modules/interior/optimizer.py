"""
Genetic Algorithm Optimizer for Interior Design
"""

import random
import copy
import torch
import os
import numpy as np
from .geometry import create_furniture_polygon
from .constraints import ConstraintChecker
from .fitness import FitnessEvaluator
from .ml.model import InteriorFitnessModel

class GeneticOptimizer:
    def __init__(self, room_poly, furniture_items, population_size=50, generations=100):
        self.room_poly = room_poly
        self.furniture_items = furniture_items
        self.pop_size = population_size
        self.generations = generations
        self.constraints = ConstraintChecker(room_poly, [], []) # TODO: Pass doors/windows
        self.evaluator = FitnessEvaluator(room_poly, furniture_items, self.constraints)
        
        # Room bounds for random initialization
        self.min_x, self.min_y, self.max_x, self.max_y = room_poly.bounds
        
        # Load ML Model
        self.ml_model = None
        self.device = torch.device("cpu")
        try:
            model_path = os.path.join(os.path.dirname(__file__), "ml/models/best_model.pth")
            if os.path.exists(model_path):
                # Calculate input size: 5 base features + 2 layout features (avg_x, avg_y)
                input_size = 7 
                self.ml_model = InteriorFitnessModel(input_size=input_size)
                self.ml_model.load_state_dict(torch.load(model_path, map_location=self.device))
                self.ml_model.eval()
                print("ML Model loaded successfully for hybrid optimization.")
            else:
                print("ML Model not found. Using pure geometric optimization.")
        except Exception as e:
            print(f"Failed to load ML model: {e}")

    def create_individual(self):
        """Create a random layout"""
        layout = []
        for item in self.furniture_items:
            # Random position within bounds
            x = random.uniform(self.min_x, self.max_x)
            y = random.uniform(self.min_y, self.max_y)
            # Random rotation (0, 90, 180, 270)
            rot = random.choice([0, 90, 180, 270]) if item.get("rotatable", True) else 0
            layout.append((x, y, rot))
        return layout

    def crossover(self, parent1, parent2):
        """Single point crossover"""
        point = random.randint(1, len(self.furniture_items) - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2

    def mutate(self, individual, mutation_rate=0.1):
        """Randomly move or rotate furniture"""
        for i in range(len(individual)):
            if random.random() < mutation_rate:
                x, y, rot = individual[i]
                # Small move
                x += random.uniform(-0.5, 0.5)
                y += random.uniform(-0.5, 0.5)
                # Random rotation change
                if random.random() < 0.5:
                    rot = random.choice([0, 90, 180, 270])
                individual[i] = (x, y, rot)
        return individual

    def _get_ml_score(self, individual):
        """Predict fitness using ML model"""
        if not self.ml_model:
            return 0.0
            
        # Extract features (Simplified for now, matching train.py logic)
        # In a real app, we should share feature extraction code
        room_area = self.room_poly.area / 50.0
        aspect_ratio = 1.0 # Placeholder
        num_doors = 0.25 # Placeholder
        num_windows = 0.25 # Placeholder
        num_furniture = len(self.furniture_items) / 20.0
        
        # Layout features
        xs = [item[0] for item in individual]
        ys = [item[1] for item in individual]
        avg_x = sum(xs) / len(xs)
        avg_y = sum(ys) / len(ys)
        
        width = self.max_x - self.min_x
        height = self.max_y - self.min_y
        norm_avg_x = avg_x / width if width > 0 else 0
        norm_avg_y = avg_y / height if height > 0 else 0
        
        features = [room_area, aspect_ratio, num_doors, num_windows, num_furniture, norm_avg_x, norm_avg_y]
        tensor_in = torch.tensor([features], dtype=torch.float32).to(self.device)
        
        with torch.no_grad():
            score = self.ml_model(tensor_in).item()
            
        # Denormalize score (model output is roughly -1 to 1)
        return score * 100.0

    def optimize(self):
        """Run the genetic algorithm"""
        # Initialize population
        population = [self.create_individual() for _ in range(self.pop_size)]
        
        best_solution = None
        best_fitness = float('-inf')
        
        for gen in range(self.generations):
            # Evaluate fitness
            fitness_scores = []
            for ind in population:
                geo_score = self.evaluator.calculate_fitness(ind)
                
                if self.ml_model:
                    ml_score = self._get_ml_score(ind)
                    # Hybrid Score: 70% Geometry (Hard Constraints), 30% ML (Heuristics)
                    final_score = (geo_score * 0.7) + (ml_score * 0.3)
                else:
                    final_score = geo_score
                    
                fitness_scores.append(final_score)
            
            # Track best
            max_fitness = max(fitness_scores)
            if max_fitness > best_fitness:
                best_fitness = max_fitness
                best_solution = population[fitness_scores.index(max_fitness)]
                
            # Selection (Tournament)
            new_population = []
            while len(new_population) < self.pop_size:
                # Select 2 parents
                p1 = population[random.randint(0, self.pop_size-1)]
                p2 = population[random.randint(0, self.pop_size-1)]
                
                # Crossover
                c1, c2 = self.crossover(p1, p2)
                
                # Mutate
                c1 = self.mutate(c1)
                c2 = self.mutate(c2)
                
                new_population.extend([c1, c2])
                
            population = new_population[:self.pop_size]
            
        return best_solution, best_fitness
