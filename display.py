import base64
import time
from io import StringIO
from utils import plot_solution, plot_solution_2, plot_units
from solver import Greedy, Genetics, DP, MIP
from generate_data import generate_data
import streamlit as st
from functools import partial
import matplotlib.pyplot as plt
import pandas as pd


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
    st.session_state['output'] = [{}, {}, {}, {}]


def summary():
    results = []
    f = 0
    for file in multiple_files:
        strio = StringIO(file.getvalue().decode("utf-8"), newline='\n')
        string_data = strio.read().splitlines()
        areas_demand = []
        units = []
        i = 0
        sparcity, radius, number_of_areas, number_of_units_per_area, \
        budget, r = [int(x) for x in string_data[i].split(" ")]
        i += 1
        while i < number_of_areas + 1:
            x, y, demand = [int(x) for x in string_data[i].split(" ")]
            areas_demand.append([(x, y), demand])
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
        # Greedy
        start = time.time()
        algo1_sol = Greedy(units, areas_demand, budget, radius, 1, r)
        algo1_t = time.time() - start
        _, algo1_z, algo1_c = plot_solution(algo1_sol, units, areas_demand, radius)
        # Genetics
        start = time.time()
        algo2_c, algo2_z, _ = Genetics(units, areas_demand, budget, radius, 1, r)
        algo2_t = time.time() - start
        # DP
        start = time.time()
        algo3_c, algo3_z1, algo3_z2, _ = DP(units, areas_demand, budget, radius, 1, r)
        algo3_z = algo3_z1 + algo3_z2
        algo3_t = time.time() - start
        # MIP
        start = time.time()
        algo4_sol = MIP(units, areas_demand, budget, radius, 1, r)
        algo4_t = time.time() - start
        _, algo4_z, algo4_c = plot_solution(algo4_sol, units, areas_demand, radius)
        # result
        results.append([f, len(units), budget,
                        algo1_c, algo1_z, algo1_t,
                        algo2_c, algo2_z, algo2_t,
                        algo3_c, algo3_z, algo3_t,
                        algo4_c, algo4_z, algo4_t])
        f += 1
    columns = ['test_case', 'number_of_units', 'budget',
               'algo1_c', 'algo1_z', 'algo1_t',
               'algo2_c', 'algo2_z', 'algo2_t',
               'algo3_c', 'algo3_z', 'algo3_t',
               'algo4_c', 'algo4_z', 'algo4_t']
    df_results = pd.DataFrame(results, columns=columns)
    csv = df_results.to_csv(index=False).encode()
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="download.csv">Download summary file</a>'
    return href



def solve(s):
    units = st.session_state['units']
    areas_demand = st.session_state['areas_demand']
    cpd = 1
    if s == 'Greedy':
        t = time.time()
        solution = Greedy(units, areas_demand, budget, radius, cpd, r)
        st.session_state['fig'], customer, cost, kitchens,restaurants,path = plot_solution(solution, units, areas_demand, radius)
        st.session_state['output'][0] = {'Algo': 'Greedy', 'customers': customer, 'cost': cost, 'time': time.time() - t}
    elif s == 'Genetics':
        t = time.time()
        solution = Genetics(units, areas_demand, budget, radius, cpd, r)
        st.session_state['fig'],kitchens,restaurants,path = plot_solution_2(solution[3], units, areas_demand, radius)
        st.session_state['output'][1] = {'Algo': 'Genetics', 'customers': solution[0], 'cost': solution[1]+solution[2],
                                         'time': time.time() - t}
    elif s == 'DP':
        t = time.time()
        solution = DP(units, areas_demand, budget, radius, cpd, r)
        st.session_state['fig'],kitchens,restaurants,path = plot_solution_2(solution[3], units, areas_demand, radius)
        st.session_state['output'][2] = {'Algo': 'DP', 'customers': solution[0], 'cost': solution[1] + solution[2],
                                         'time': time.time() - t}
    elif s == 'MIP':
        t = time.time()
        solution = MIP(units, areas_demand, budget, radius, cpd, r)
        st.session_state['fig'], customer, cost,kitchens,restaurants,path = plot_solution(solution, units, areas_demand, radius)
        st.session_state['output'][3] = {'Algo': 'MIP', 'customers': customer, 'cost': cost, 'time': time.time() - t}


if 'units' not in st.session_state:
    units, areas_demand = generate_data()
    st.session_state['units'] = units
    st.session_state['areas_demand'] = areas_demand
    st.session_state['fig'] = plt.figure()
if 'output' not in st.session_state:
    st.session_state['output'] = [{}, {}, {}, {}]

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
    multiple_files = st.file_uploader("Multiple File Uploader", accept_multiple_files=True)
    st.markdown(summary(), unsafe_allow_html=True)
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
    budget = st.slider('Total budget', int(1e6), int(1e8), int(1e6), step=int(1e6), format="%e")
    r = st.slider('Optimization ratio', int(1e6), int(1e9), int(1e6), step=int(1e6), format="%e")
    st.button('Generate Random Data', on_click=get_units)

with right:
    st.pyplot(st.session_state['fig'], clear_figure=True)
    st.button('Greedy', on_click=partial(solve, 'Greedy'))
    st.button('Genetics', on_click=partial(solve, 'Genetics'))
    st.button('DP', on_click=partial(solve, 'DP'))
    st.button('MIP', on_click=partial(solve, 'MIP'))
    st.header("Areas & Demands")
    df_areas_demand = pd.DataFrame.from_dict(st.session_state['areas_demand'])
    df_areas_demand.columns = ['center', 'area_demand']
    st.dataframe(df_areas_demand)
    st.header("Units Info.")
    st.dataframe(pd.DataFrame.from_dict(st.session_state['units']))
    st.header("Results")
    st.dataframe(pd.DataFrame.from_dict(st.session_state['output']))
