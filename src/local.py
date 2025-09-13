from dataclasses import dataclass
from typing import List, Optional
import random
import numpy as np
from .metrics import Metrics
from random import choice
from .model import DomainManager, rc_to_idx

Grid = List[List[int]]


@dataclass
class SAConfig:
    domain_manager: DomainManager
    seed: int = 0
    max_steps: int = 100000
    restarts: int = 200
    temperature: float = 1.0
    cooling: float = 0.95

def saFitness(grid):
    total = 0
    for i in range(9):
        col_i = [grid[r][i] for r in range(9)]
        row_i = grid[i]
        total += (9 - len(set(col_i))) + (9 - len(set(row_i)))
    return total

def getBlocks(grid):
    answer = []
    for r in range(3):
        for c in range(3):
            block = []
            for i in range(3):
                for j in range(3):
                    block.append(grid[3*r + i][3*c + j])
            answer.append(block)
    return answer

def fillrandom(blocks):
    for block in blocks:
        for j in range(0,9):
            if block[j] == 0:
                    block[j] = choice([i for i in range(1,10) if i not in block])
    randomgrid = []
    for block_row in range(3):
        for row_in_block in range(3):
            row = []
            for block_col in range(3):
                block_index = block_row * 3 + block_col
                row.extend(blocks[block_index][row_in_block*3 : (row_in_block+1)*3])
            randomgrid.append(row)
    randomgrid = np.array(randomgrid)
    return randomgrid


def flip(gridtemp, domain_manager):
    temporary = gridtemp.copy()
    while True:
        row1 = random.randint(0, 8)
        col1 = random.randint(0, 8)
        while True:
            r = (row1 // 3) * 3 + random.randint(0, 2)
            c = (col1 // 3) * 3 + random.randint(0, 2)
            if (r, c) != (row1, col1):
                row2 = r
                col2 = c
                break
        if rc_to_idx(row1, col1) not in domain_manager.fixed_values and rc_to_idx(row2, col2) not in domain_manager.fixed_values:
            # print(f"Swapping ({row1},{col1}) with ({row2},{col2})")
            temp = temporary[row1][col1]
            temporary[row1][col1] = temporary[row2][col2]
            temporary[row2][col2] = temp
            return temporary


def solve_sa(initial_grid: Grid, cfg: SAConfig, metrics: Metrics) -> Optional[Grid]:
    current_grid = fillrandom(getBlocks(initial_grid))
    stuck_count = 0
    for i in range (cfg.max_steps):
        for j in range(cfg.restarts):
            stuck_count += 1
            metrics.decisions += 1
            newgrid = flip(current_grid, cfg.domain_manager)
            metrics.sa_fitness_curve.append(saFitness(current_grid))
            if saFitness(newgrid) < saFitness(current_grid):
                current_grid = newgrid
                print("Accepted better solution")
            else:
                acceptance_probability = np.exp((saFitness(current_grid) - saFitness(newgrid)) / cfg.temperature)
                if random.random() < acceptance_probability:
                    current_grid = newgrid
                    print("Accepted worse solution")
            print(f"current fitness: {saFitness(current_grid)}")
            if saFitness(current_grid) == 0:
                print("Solution found")
                print(f"Total loops: {metrics.decisions}")
                print(current_grid)
                return current_grid
            print(saFitness(current_grid), metrics.restarts, metrics.decisions)
        cfg.temperature = cfg.temperature * cfg.cooling
        print(f"End of iteration, temperature: {cfg.temperature}")
        if stuck_count == 15000:
        #current_grid = fillrandom(blocks)
            stuck_count = 0
            print("Restarting with new random grid")
            cfg.temperature = cfg.temperature + 2
        if saFitness(current_grid) == 0:
            return current_grid
    return None


@dataclass
class GAConfig:
    domain_manager: DomainManager
    seed: int = 0
    population_size: int = 200
    generations: int = 2000
    tournament_k: int = 3
    mutation_rate: float = 0.5
    elitism: int = 2

def gaFitness(grid):
    ErrorCount = 0
    total = 0
    for i in range(0,9):
        ErrorCount = (9 - len(np.unique(grid[:,i]))) + (9 - len(np.unique(grid[i,:])))
        total = total + ErrorCount
    for i in range(0,3):
        for j in range(0,3):
            ErrorCount = 9 - len(np.unique(grid[i*3:(i*3)+3,j*3:(j*3)+3]))
            total = total + ErrorCount
    return total

def mutate(gridtemp , domain_manager):
    temporary = gridtemp.copy()
    while True:
        row1 =  random.randint(0,8)
        col1 =  random.randint(0,8)
        if rc_to_idx(row1, col1) not in domain_manager.fixed_values:
            if random.random() < 1:
                temporary[row1][col1] = random.randint(1,9)
            break
    return temporary

def population_initial(grid, flag):
    temp = grid.copy()
    for i in range(0,9):
        for j in range(0,9):
            if rc_to_idx(i, j) not in domain_manager.fixed_values:
                temp[i][j] = random.randint(1,9)
    return temp

def population_initial_update(grid):
    tempgrid = grid.copy()
    blocks = []
    for r in range(3):
        for c in range(3):
            block = []
            for i in range(3):
                for j in range(3):
                    block.append(tempgrid[3*r + i][3*c + j])
            blocks.append(block)
    for block in blocks:
        for j in range(0,9):
            if block[j] == 0:
                    block[j] = choice([i for i in range(1,10) if i not in block])
    randomgrid = []
    for block_row in range(3):
        for row_in_block in range(3):
            row = []
            for block_col in range(3):
                block_index = block_row * 3 + block_col
                row.extend(blocks[block_index][row_in_block*3 : (row_in_block+1)*3])
            randomgrid.append(row)
    randomgrid = np.array(randomgrid)
    return randomgrid

def tournament_selection(population, fitnesses):
    tournament_size = 3
    selected_indices = random.sample(range(len(population)), tournament_size)
    selected = [population[i] for i in selected_indices]
    selected_fitnesses = [fitnesses[i] for i in selected_indices]
    winner_index = selected_indices[selected_fitnesses.index(min(selected_fitnesses))]
    return population[winner_index]

def crossover(parent1, parent2, domain_manager):
    child1 = parent1.copy()
    child2 = parent2.copy()
    row = random.randint(0,8)
    col = random.randint(0,8)
    for i in range(row,9):
        for j in range(col,9):
            if rc_to_idx(i, j) not in domain_manager.fixed_values:
                child1[i][j] = parent2[i][j]
                child2[i][j] = parent1[i][j]
    return child1,child2

def solve_ga(initial_grid: Grid, cfg: GAConfig, metrics: Metrics) -> Optional[Grid]:
    first_gen = []
    for p in range(0, cfg.population_size):
        temp = population_initial(initial_grid.copy(),cfg.domain_manager)
        temp = np.array(temp)
        first_gen.append(temp.copy())
    current_gen = first_gen
    current_gen = np.array(current_gen)
    for generation in range(10000):
        metrics.generations += 1
        print(f"Generation {generation + 1}")
        fitness_list = []
        next_gen = []
        for individual in current_gen:
            fitness_list.append(gaFitness(individual))
        average = sum(fitness_list) / len(fitness_list)
        print("Average Fitness: ", average)
        print("Best Fitness: ", min(fitness_list))
        if 0 in fitness_list:
            index = fitness_list.index(0)
            print("Solution Found")
            print(current_gen[index])
            break
        for i in range(50):
            parent1 = tournament_selection(current_gen, fitness_list)
            parent2 = tournament_selection(current_gen, fitness_list)
            [child1,child2] = crossover(parent1, parent2, cfg.domain_manager)
            child1 = mutate_update(child1,cfg.domain_manager)
            child2 = mutate_update(child2,cfg.domain_manager)
            next_gen.append(child1)
            next_gen.append(child2)
            # print("%d pairs created\n"%(i+1))
            # print("NextGen Size: ",len(next_gen))
        best_fit = min(fitness_list)
        metrics.ga_fitness_curve.append(best_fit)
        current_gen = next_gen
        print(len(current_gen))
    return None
