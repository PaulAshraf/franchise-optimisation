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
        return "Rent increases with demand"
    if i == 2:
        return "Capaicty increases with rent + Rent increases with demand"


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
        sparcity, radius, num_units_per_area, a, budget, r, u = [int(x) for x in string_data[0].split(" ")]
        for i in range(1, int(a) + 1):
            x, y, demand = [int(x) for x in string_data[i].split(" ")]
            areas.append([(x, y), demand])
        for i in range(1 + int(a), 1 + int(a) + int(u)):
            x, y, j, area, rent, capacity_kitchen, capacity_restaurant, initial_restaurant, initial_kitchen = [int(x)
                                                                                                               for x in
                                                                                                               string_data[
                                                                                                                   i].split(
                                                                                                                   " ")]
            units.append({
                'position': (x, y),
                'area': area,
                'rent': rent,
                'capacity_kitchen': capacity_kitchen,
                'capacity_restaurant': capacity_restaurant,
                'initial_restaurant': initial_restaurant,
                'initial_kitchen': initial_kitchen,
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
        st.session_state['fig'] = plot_solution(solution, units, areas_demand, radius)
    elif s == 'Genetics':
        solution = Genetics(units, areas_demand, budget, radius, cpd, r)
        st.session_state['fig'] = plot_solution_2(solution[2], units, areas_demand, radius)
    elif s == 'DP':
        solution = DP(units, areas_demand, budget, radius, cpd, r)
        st.session_state['fig'] = plot_solution_2(solution[3], units, areas_demand, radius)
    elif s == 'MIP':
        solution = MIP(units, areas_demand, budget, radius, cpd, r)
        st.session_state['fig'] = plot_solution(solution, units, areas_demand, radius)


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

        First line: sparcity, radius, num\_units\_per\_area, areas(a), budget, r, units(n)
        
        _For n lines_: x, y, j, area, rent, capacity\_kitchen, capacity\_restaurant, initial\_restaurant, initial\_kitchen
        
        _For a lines_: x, y, demand

    ''')
    file = st.file_uploader('Upload File')
    st.button('Generate Data from File', on_click=get_units_from_file)
    st.header('Random Data')
    sparcity = st.slider('Sparcity', -20, 20, -10)
    radius = st.slider('Radius', 0, 20, 10)
    num_units_per_area = st.slider('Number of units per area range', 1, 6, (2, 3))
    areas = st.slider('Areas', 0, 8, 6)
    demand_range = st.slider('Demand Range', 0, 2000, (1000, 1500), step=50)
    rent_range = st.slider('Rent Range', 0, 20000, (3000, 15000), step=100)
    capacity_kitchen_range = st.slider('Kitchen Capacity Range', 0, 5000, (1000, 1500), step=100)
    capacity_restaurant_range = st.slider('Restaurant Capacity Range', 0, 1000, (250, 500), step=50)
    initial_kitchen_range = st.slider('Kitchen Initial Cost Range', 0, 2000000, (500000, 1000000), step=10000)
    initial_restaurant_range = st.slider('Restaurant Initial Cost Range', 0, 1000000, (100000, 200000), step=10000)
    budget = st.slider('Budget', int(4e6), int(1e9), int(4e6), step=int(1e6), format="%e")
    r = st.slider('Optimisation Ratio', int(1e3), int(1e9), int(1e3), step=int(1e6), format="%e")
    scenario = st.radio('Scenario', range(3), format_func=scenarios)
    st.button('Generate Random Data', on_click=get_units)

with right:
    st.button('Greedy', on_click=partial(solve, 'Greedy'))
    st.button('Genetics', on_click=partial(solve, 'Genetics'))
    st.button('DP', on_click=partial(solve, 'DP'))
    st.button('MIP', on_click=partial(solve, 'MIP'))
    st.pyplot(st.session_state['fig'], clear_figure=True)
