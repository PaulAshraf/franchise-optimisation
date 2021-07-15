from io import StringIO
from utils import plot_solution
from solver import mip
from generate_data import generate_data, plot_units
import streamlit as st
import matplotlib.pyplot as plt
from functools import partial

def scenarios(i):
    if i == 0:
        return "No Correlations (Tottaly Random)"
    if i == 1:
        return "Rent increases with demand"
    if i == 2:
        return "Capaicty increases with rent + Rent increases with demand"

def get_units():
    units, areas_demand = generate_data(sparcity,
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
            x, y, j, area, rent, capacity_kitchen, capacity_restaurant, initial_restaurant, initial_kitchen = [int(x) for x in string_data[i].split(" ")]
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
        print(units)
        print(areas)
        st.session_state['units'] = units
        st.session_state['areas_demand'] = areas
        fig = plot_units(units, areas, radius)
        st.session_state['fig'] = fig
        
            

def solve(solver):
    if solver == 'mip':
        solution = mip(st.session_state['units'], st.session_state['areas_demand'], radius=radius, budget=budget, cpd=1, r=r)
        fig = plot_solution(solution, st.session_state['units'], st.session_state['areas_demand'])
        st.session_state['fig'] = fig


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
    sparcity = st.slider('Sparcity', 0, 100, 15)
    radius = st.slider('Radius', 0, 100, 10)
    num_units_per_area = st.slider('Number of units per area range', 0, 20, (2, 3))
    areas = st.slider('Areas', 0, 10, 6)
    demand_range = st.slider('Demand Range', 0, int(1e9), (int(4e8), int(7e8)), step=10000, format="%e")
    rent_range = st.slider('Rent Range', 0, 20000, (3000, 15000), step=10)
    capacity_kitchen_range = st.slider('Kitchen Capacity Range', 0, 20000, (2000, 3000), step=10)
    capacity_restaurant_range = st.slider('Restaurant Capacity Range', 0, 1000, (300, 400), step=10)
    initial_kitchen_range = st.slider('Kitchen Initial Cost Range', 0, 2000000, (500000, 1000000), step=10000)
    initial_restaurant_range = st.slider('Restaurant Initial Cost Range', 0, 1000000, (100000, 200000), step=10000)
    budget = st.slider('Budget', 0, int(1e7), int(5e6), step=10000)
    r = st.slider('Optimisation Ratio', 0, int(1e3), 10, step=10)
    scenario = st.radio('Scenario', range(3), format_func=scenarios)
    st.button('Generate Random Data', on_click=get_units)

with right:
    st.button('Solve w/ MIP', on_click=partial(solve, 'mip'))
    st.pyplot(st.session_state['fig'], clear_figure=True)


