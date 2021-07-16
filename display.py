from io import StringIO
from utils import plot_solution, plot_solution_2, plot_units
from solver import Greedy, Genetics, DP, MIP
from generate_data import generate_data
import streamlit as st
from functools import partial
import matplotlib.pyplot as plt


def scenarios(i):
    if i == 0:
        return "No Correlations (Tottaly Random)"
    if i == 1:
        return "Rent increases with area demand"
    if i == 2:
        return "Capacity increases with rent price & Rent increases with area demand"


def get_units():
    units, areas_demand = generate_data(scenario,
                                        sparcity,
                                        radius,
                                        num_units_per_area,
                                        areas,
                                        demand_range,
                                        rent_range,
                                        capacity_kitchen_range,
                                        capacity_restaurant_range,
                                        initial_kitchen_range,
                                        initial_restaurant_range
                                        )
    st.session_state['units'] = units
    st.session_state['areas_demand'] = areas_demand
    fig = plot_units(units, areas_demand, radius)
    st.session_state['fig'] = fig


def get_units_from_file():
    if file is not None:
        strio = StringIO(file.getvalue().decode("utf-8"), newline='\n')
        string_data = strio.read().splitlines()
        areas = []
        units = []
        i = 0
        sparcity, radius, number_of_areas, number_of_units_per_area, \
        budget, optimization_ratio = [int(x) for x in string_data[i].split(" ")]
        i += 1
        while i < number_of_areas + 1:
            x, y, demand = [int(x) for x in string_data[i].split(" ")]
            areas.append([(x, y), demand])
            i += 1
        for j in range(number_of_areas * number_of_units_per_area):
            point_x, point_y, area_number, rent, if_kitchen_capacity, if_restaurant_capacity, \
            if_restaurant_initial_price, if_kitchen_initial_price = [int(x) for x in string_data[j + i].split(" ")]
            units.append({
                'position': (point_x, point_y),
                'area': area_number - 1,
                'rent': rent,
                'capacity_kitchen': if_kitchen_capacity,
                'capacity_restaurant': if_restaurant_capacity,
                'initial_restaurant': if_restaurant_initial_price,
                'initial_kitchen': if_kitchen_initial_price,
                'initial_index': j
            })
        st.session_state['units'] = units
        st.session_state['areas_demand'] = areas
        fig = plot_units(units, areas, radius)
        st.session_state['fig'] = fig


def solve(s):
    units = st.session_state['units']
    areas_demand = st.session_state['areas_demand']
    cpd = 1
    if s == 'Greedy':
        solution = Greedy(units, areas_demand, budget, radius, cpd, r)
        st.session_state['fig'], customer, cost = plot_solution(solution, units, areas_demand, radius)
        print('Greedy', customer, cost)
    elif s == 'Genetics':
        solution = Genetics(units, areas_demand, budget, radius, cpd, r)
        print('Genetics', solution[0], solution[1])
        st.session_state['fig'] = plot_solution_2(solution[2], units, areas_demand, radius)
    elif s == 'DP':
        solution = DP(units, areas_demand, budget, radius, cpd, r)
        print('DP', solution[0], solution[1] + solution[2])
        st.session_state['fig'] = plot_solution_2(solution[3], units, areas_demand, radius)
    elif s == 'MIP':
        solution = MIP(units, areas_demand, budget, radius, cpd, r)
        st.session_state['fig'], customer, cost = plot_solution(solution, units, areas_demand, radius)
        print('MIP', customer, cost)


if 'units' not in st.session_state:
    units, areas_demand = generate_data()
    st.session_state['units'] = units
    st.session_state['areas_demand'] = areas_demand
    st.session_state['fig'] = plt.figure()

st.set_page_config(layout='wide')
st.set_option('deprecation.showPyplotGlobalUse', False)
left, right = st.beta_columns(2)

with left:
    st.title('Input Data')
    st.header('Upload Your Own Dataset')
    st.markdown(r''' 

        The input file should be using the following format:

        _First line_:
        
            sparcity, radius, number_of_areas, number_of_units_per_area, budget, optimization_ratio
        
        _For number_of_areas lines_:
        
            center_x, center_y, demand_per_area
        
        _For (number_of_units_per_area*number_of_areas) lines_:
        
            point_x, point_y, area_number, rent, if_kitchen_capacity, if_restaurant_capacity, if_restaurant_initial_price,
            if_kitchen_initial_price

    ''')
    file = st.file_uploader('Upload File')
    st.button('Generate Data from File', on_click=get_units_from_file)
    st.header('Random Data')
    sparcity = st.slider('Sparcity', -20, 20, -10)
    radius = st.slider('Radius', 0, 20, 10)
    areas = st.slider('Number of areas', 0, 8, 6)
    num_units_per_area = st.slider('Number of units per area', 1, 6, (2, 3))
    demand_range = st.slider('Demand range per area', 0, 2000, (1000, 1500), step=50)
    rent_range = st.slider('Rent range per area', 0, 20000, (3000, 15000), step=100)
    capacity_kitchen_range = st.slider('Kitchen capacity range for all kitchens', 0, 5000, (1000, 1500), step=100)
    capacity_restaurant_range = st.slider('Restaurant capacity range for all restaurants', 0, 1000, (250, 500), step=50)
    initial_kitchen_range = st.slider('Kitchen initial cost range for all kitchens', 0, 2000000, (500000, 1000000),
                                      step=10000)
    initial_restaurant_range = st.slider('Restaurant initial cost range for all restaurants', 0, 1000000,
                                         (100000, 200000), step=10000)
    budget = st.slider('Total budget', int(4e6), int(1e9), int(4e6), step=int(1e6), format="%e")
    r = st.slider('Optimization ratio', int(1e6), int(1e9), int(1e6), step=int(1e6), format="%e")
    scenario = st.radio('Scenario', range(3), format_func=scenarios)
    st.button('Generate Random Data', on_click=get_units)

with right:
    st.pyplot(st.session_state['fig'], clear_figure=True)
    st.button('Greedy', on_click=partial(solve, 'Greedy'))
    st.button('Genetics', on_click=partial(solve, 'Genetics'))
    st.button('DP', on_click=partial(solve, 'DP'))
    st.button('MIP', on_click=partial(solve, 'MIP'))
