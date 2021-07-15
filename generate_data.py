from utils import get_random, get_random_positions, get_random_areas


def generate_data(
        scenario=0,
        sparcity=-10,
        radius=10,
        num_units_per_area=(1, 2),
        areas=6,
        demand_range=(1000, 1500),
        rent_range=(3000, 15000),
        capacity_kitchen_range=(1000, 1500),
        capacity_restaurant_range=(250, 500),
        initial_kitchen_range=(500000, 1000000),
        initial_restaurant_range=(100000, 200000)):
    units = []
    areas_demand = []
    j = 0
    for i, area in enumerate(get_random_areas(areas, sparcity, radius)):
        demand = get_random(demand_range)
        areas_demand.append((area, demand))
        positions = get_random_positions(area, radius, get_random(num_units_per_area))
        for pos in positions:
            units.append({
                'position': pos,
                'area': i,
                'rent': get_random(rent_range),
                'capacity_kitchen': get_random(capacity_kitchen_range),
                'capacity_restaurant': get_random(capacity_restaurant_range),
                'initial_restaurant': get_random(initial_restaurant_range),
                'initial_kitchen': get_random(initial_kitchen_range),
                'initial_index': j
            })
            j += 1
    return units, areas_demand
