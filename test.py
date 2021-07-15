from generate_data import generate_data
from solver import Greedy, Genetics, DP, MIP

if __name__ == '__main__':
    areas = 6
    radius = 10
    budget = int(4e6)
    r = 1e6
    cpd = 1
    units, areas_demand = generate_data(
        areas=areas,
        radius=radius,
        demand_range=(1000, 1500),
        capacity_kitchen_range=(1000, 1500),
        capacity_restaurant_range=(250, 500),
        num_units_per_area=(1, 2),
        sparcity=-10)
    n = len(units)
    solution = Genetics(units, areas_demand, budget, radius, cpd, r)
    print(solution)
    solution = DP(units, areas_demand, budget, radius, cpd, r)
    print(solution)
