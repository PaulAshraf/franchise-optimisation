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
import gc


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
    st.session_state['algo1_fig'] = fig
    st.session_state['algo2_fig'] = fig
    st.session_state['algo3_fig'] = fig
    st.session_state['algo4_fig'] = fig
    n = len(units)
    st.session_state['output'] = \
        {'number_of_units': n, 'budget': budget,
         'algo1_cust': '', 'algo1_cost': '', 'algo1_trans': '', 'algo1_util': '', 'algo1_missed': '',
         'algo1_dist_meal': '', 'algo1_t': '',
         'algo2_cust': '', 'algo2_cost': '', 'algo2_trans': '', 'algo2_util': '', 'algo2_missed': '',
         'algo2_dist_meal': '', 'algo2_t': '',
         'algo3_cust': '', 'algo3_cost': '', 'algo3_trans': '', 'algo3_util': '', 'algo3_missed': '',
         'algo3_dist_meal': '', 'algo3_t': '',
         'algo4_cust': '', 'algo4_cost': '', 'algo4_trans': '', 'algo4_util': '', 'algo4_missed': '',
         'algo4_dist_meal': '', 'algo4_t': ''}
    st.session_state['algo1_output_units'] = {}
    st.session_state['algo1_output_trans'] = [[0 for _ in range(n)] for _ in range(n)]
    st.session_state['algo2_output_units'] = {}
    st.session_state['algo2_output_trans'] = [[0 for _ in range(n)] for _ in range(n)]
    st.session_state['algo3_output_units'] = {}
    st.session_state['algo3_output_trans'] = [[0 for _ in range(n)] for _ in range(n)]
    st.session_state['algo4_output_units'] = {}
    st.session_state['algo4_output_trans'] = [[0 for _ in range(n)] for _ in range(n)]


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
        t = time.time()
        solution = Greedy(units, areas_demand, budget, radius, 1, r)
        algo1_t = time.time() - t
        algo1_fig, algo1_cust, algo1_cost, algo1_trans, algo1_kitchens, algo1_restaurants, algo1_path, algo1_util, \
        algo1_dist_meal = plot_solution(solution, units, areas_demand, radius)
        # Genetics
        t = time.time()
        algo2_cust, algo2_cost, algo2_trans, algo2_plot = Genetics(units, areas_demand, budget, radius, 1, r)
        algo2_t = time.time() - t
        algo2_fig, algo2_kitchens, algo2_restaurants, algo2_path, algo2_util = \
            plot_solution_2(algo2_plot, units, areas_demand, radius)
        # DP
        useBudgetApproximation = min(if_kitchen_initial_price, if_restaurant_initial_price)
        t = time.time()
        algo3_cust, algo3_cost, algo3_trans, algo3_plot = DP(units, areas_demand, budget, radius, 1, r,
                                                             useBudgetApproximation)
        algo3_t = time.time() - t
        algo3_fig, algo3_kitchens, algo3_restaurants, algo3_path, algo3_util = \
            plot_solution_2(algo3_plot, units, areas_demand, radius)
        # MIP
        t = time.time()
        solution = MIP(units, areas_demand, budget, radius, 1, r)
        algo4_t = time.time() - t
        algo4_fig, algo4_cust, algo4_cost, algo4_trans, algo4_kitchens, algo4_restaurants, algo4_path, algo4_util, \
        algo4_dist_meal = plot_solution(solution, units, areas_demand, radius)
        # result
        results.append([
            f, len(units), budget,
            algo1_cust, algo1_cost, algo1_trans, algo1_util, 100 - algo1_util, algo1_dist_meal, algo1_t,
            algo2_cust, algo2_cost, algo2_trans, algo2_util, 100 - algo2_util, algo2_trans / algo2_cust, algo2_t,
            algo3_cust, algo3_cost, algo3_trans, algo3_util, 100 - algo3_util, algo3_trans / algo3_cust, algo3_t,
            algo4_cust, algo4_cost, algo4_trans, algo4_util, 100 - algo4_util, algo4_dist_meal, algo4_t])
        f += 1
    columns = [
        'test_case', 'number_of_units', 'budget',
        'algo1_cust', 'algo1_cost', 'algo1_trans', 'algo1_util', 'algo1_missed', 'algo1_dist_meal', 'algo1_t',
        'algo2_cust', 'algo2_cost', 'algo2_trans', 'algo2_util', 'algo2_missed', 'algo2_dist_meal', 'algo2_t',
        'algo3_cust', 'algo3_cost', 'algo3_trans', 'algo3_util', 'algo3_missed', 'algo3_dist_meal', 'algo3_t',
        'algo4_cust', 'algo4_cost', 'algo4_trans', 'algo4_util', 'algo4_missed', 'algo4_dist_meal', 'algo4_t']
    df_results = pd.DataFrame(results, columns=columns)
    csv = df_results.to_csv(index=False).encode()
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="download.csv">Download summary file</a>'
    return href


def solve(s):
    gc.collect()
    units = st.session_state['units']
    areas_demand = st.session_state['areas_demand']
    cpd = 1
    if s == 'Greedy':
        t = time.time()
        solution = Greedy(units, areas_demand, budget, radius, cpd, r)
        algo1_t = time.time() - t
        algo1_fig, algo1_cust, algo1_cost, algo1_trans, algo1_kitchens, algo1_restaurants, algo1_path, algo1_util, \
        algo1_dist_meal = plot_solution(solution, units, areas_demand, radius)
        st.session_state['algo1_fig'] = algo1_fig
        st.session_state['output']['algo1_cust'] = algo1_cust
        st.session_state['output']['algo1_cost'] = algo1_cost
        st.session_state['output']['algo1_trans'] = algo1_trans
        st.session_state['output']['algo1_util'] = algo1_util
        st.session_state['output']['algo1_missed'] = 100 - algo1_util
        st.session_state['output']['algo1_dist_meal'] = algo1_dist_meal
        st.session_state['output']['algo1_t'] = algo1_t
        output('algo1_output', algo1_kitchens, algo1_restaurants, algo1_path)
    elif s == 'Genetics':
        t = time.time()
        algo2_cust, algo2_cost, algo2_trans, algo2_plot = Genetics(units, areas_demand, budget, radius, cpd, r)
        algo2_t = time.time() - t
        algo2_fig, algo2_kitchens, algo2_restaurants, algo2_path, algo2_util = \
            plot_solution_2(algo2_plot, units, areas_demand, radius)
        st.session_state['algo2_fig'] = algo2_fig
        st.session_state['output']['algo2_cust'] = algo2_cust
        st.session_state['output']['algo2_cost'] = algo2_cost
        st.session_state['output']['algo2_trans'] = algo2_trans
        st.session_state['output']['algo2_util'] = algo2_util
        st.session_state['output']['algo2_missed'] = 100 - algo2_util
        st.session_state['output']['algo2_dist_meal'] = algo2_trans / algo2_cust
        st.session_state['output']['algo2_t'] = algo2_t
        output('algo2_output', algo2_kitchens, algo2_restaurants, algo2_path)
    elif s == 'DP':
        useBudgetApproximation = min(initial_kitchen_range[0], initial_restaurant_range[1])
        t = time.time()
        algo3_cust, algo3_cost, algo3_trans, algo3_plot = DP(units, areas_demand, budget, radius, cpd, r,
                                                             useBudgetApproximation)
        algo3_t = time.time() - t
        algo3_fig, algo3_kitchens, algo3_restaurants, algo3_path, algo3_util = \
            plot_solution_2(algo3_plot, units, areas_demand, radius)
        st.session_state['algo3_fig'] = algo3_fig
        st.session_state['output']['algo3_cust'] = algo3_cust
        st.session_state['output']['algo3_cost'] = algo3_cost
        st.session_state['output']['algo3_trans'] = algo3_trans
        st.session_state['output']['algo3_util'] = algo3_util
        st.session_state['output']['algo3_missed'] = 100 - algo3_util
        st.session_state['output']['algo3_dist_meal'] = algo3_trans / algo3_cust
        st.session_state['output']['algo3_t'] = algo3_t
        output('algo3_output', algo3_kitchens, algo3_restaurants, algo3_path)
    elif s == 'MIP':
        t = time.time()
        solution = MIP(units, areas_demand, budget, radius, cpd, r)
        algo4_t = time.time() - t
        algo4_fig, algo4_cust, algo4_cost, algo4_trans, algo4_kitchens, algo4_restaurants, algo4_path, algo4_util, \
        algo4_dist_meal = plot_solution(solution, units, areas_demand, radius)
        st.session_state['algo4_fig'] = algo4_fig
        st.session_state['output']['algo4_cust'] = algo4_cust
        st.session_state['output']['algo4_cost'] = algo4_cost
        st.session_state['output']['algo4_trans'] = algo4_trans
        st.session_state['output']['algo4_util'] = algo4_util
        st.session_state['output']['algo4_missed'] = 100 - algo4_util
        st.session_state['output']['algo4_dist_meal'] = algo4_dist_meal
        st.session_state['output']['algo4_t'] = algo4_t
        output('algo4_output', algo4_kitchens, algo4_restaurants, algo4_path)


def output(algo, kitchens, restaurants, path):
    n = st.session_state['output']['number_of_units']
    st.session_state[f'{algo}_units'] = {}
    st.session_state[f'{algo}_trans'] = [[0 for _ in range(n)] for _ in range(n)]
    for i in kitchens:
        st.session_state[f'{algo}_units'][str(i)] = 'K'
    for i in restaurants:
        st.session_state[f'{algo}_units'][str(i)] = 'R'
    for i in range(n):
        if str(i) not in st.session_state[f'{algo}_units']:
            st.session_state[f'{algo}_units'][str(i)] = 'N'
    for kitchen, restaurant, transport in path:
        st.session_state[f'{algo}_trans'][kitchen][restaurant] = transport


if 'output' not in st.session_state:
    st.session_state['output'] = \
        {'number_of_units': '', 'budget': '',
         'algo1_cust': '', 'algo1_cost': '', 'algo1_trans': '', 'algo1_util': '', 'algo1_missed': '',
         'algo1_dist_meal': '', 'algo1_t': '',
         'algo2_cust': '', 'algo2_cost': '', 'algo2_trans': '', 'algo2_util': '', 'algo2_missed': '',
         'algo2_dist_meal': '', 'algo2_t': '',
         'algo3_cust': '', 'algo3_cost': '', 'algo3_trans': '', 'algo3_util': '', 'algo3_missed': '',
         'algo3_dist_meal': '', 'algo3_t': '',
         'algo4_cust': '', 'algo4_cost': '', 'algo4_trans': '', 'algo4_util': '', 'algo4_missed': '',
         'algo4_dist_meal': '', 'algo4_t': ''}
if 'units' not in st.session_state:
    units, areas_demand = generate_data()
    st.session_state['units'] = units
    st.session_state['areas_demand'] = areas_demand
    st.session_state['output']['number_of_units'] = len(units)
if 'algo1_fig' not in st.session_state:
    st.session_state['algo1_fig'] = plt.figure()
if 'algo2_fig' not in st.session_state:
    st.session_state['algo2_fig'] = plt.figure()
if 'algo3_fig' not in st.session_state:
    st.session_state['algo3_fig'] = plt.figure()
if 'algo4_fig' not in st.session_state:
    st.session_state['algo4_fig'] = plt.figure()
if 'algo1_output_units' not in st.session_state:
    st.session_state['algo1_output_units'] = {}
    st.session_state['algo1_output_trans'] = {}
if 'algo2_output_units' not in st.session_state:
    st.session_state['algo2_output_units'] = {}
    st.session_state['algo2_output_trans'] = {}
if 'algo3_output_units' not in st.session_state:
    st.session_state['algo3_output_units'] = {}
    st.session_state['algo3_output_trans'] = {}
if 'algo4_output_units' not in st.session_state:
    st.session_state['algo4_output_units'] = {}
    st.session_state['algo4_output_trans'] = {}

st.set_page_config(layout='wide')
st.set_option('deprecation.showPyplotGlobalUse', False)
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
budget = st.slider('Total budget', int(1e6), int(1e7), int(1e6), step=int(1e6), format="%e")
st.session_state['output']['budget'] = budget
r = st.slider('Optimization ratio', int(1e6), int(1e9), int(1e6), step=int(1e6), format="%e")
st.button('Generate Random Data', on_click=get_units)
st.header('Input Tables')
st.header("Areas")
df_areas_demand = pd.DataFrame.from_dict(st.session_state['areas_demand'])
df_areas_demand.columns = ['center', 'area_demand']
st.dataframe(df_areas_demand)
st.header("Units")
st.dataframe(pd.DataFrame.from_dict(st.session_state['units']))
st.header("Greedy")
st.button('Greedy', on_click=partial(solve, 'Greedy'))
st.pyplot(st.session_state['algo1_fig'])
st.header("Genetics")
st.button('Genetics', on_click=partial(solve, 'Genetics'))
st.pyplot(st.session_state['algo2_fig'])
st.header("DP")
st.button('DP', on_click=partial(solve, 'DP'))
st.pyplot(st.session_state['algo3_fig'])
st.header("MIP")
st.button('MIP', on_click=partial(solve, 'MIP'))
st.pyplot(st.session_state['algo4_fig'])
st.header('Output Tables')
st.header('Comparison')
st.dataframe(pd.DataFrame(st.session_state['output'], index=[0], columns=[
    'number_of_units', 'budget',
    'algo1_cust', 'algo1_cost', 'algo1_trans', 'algo1_util', 'algo1_missed', 'algo1_dist_meal', 'algo1_t']))
st.dataframe(pd.DataFrame(st.session_state['output'], index=[0], columns=[
    'number_of_units', 'budget',
    'algo2_cust', 'algo2_cost', 'algo2_trans', 'algo2_util', 'algo2_missed', 'algo2_dist_meal', 'algo2_t']))
st.dataframe(pd.DataFrame(st.session_state['output'], index=[0], columns=[
    'number_of_units', 'budget',
    'algo3_cust', 'algo3_cost', 'algo3_trans', 'algo3_util', 'algo3_missed', 'algo3_dist_meal', 'algo3_t']))
st.dataframe(pd.DataFrame(st.session_state['output'], index=[0], columns=[
    'number_of_units', 'budget',
    'algo4_cust', 'algo4_cost', 'algo4_trans', 'algo4_util', 'algo4_missed', 'algo4_dist_meal', 'algo4_t']))
st.header("Greedy")
st.header("Units decision")
st.dataframe(pd.DataFrame(st.session_state['algo1_output_units'], index=[0]))
st.header("Transport decision")
st.dataframe(pd.DataFrame.from_dict(st.session_state['algo1_output_trans']))
st.header("Genetics")
st.header("Units decision")
st.dataframe(pd.DataFrame(st.session_state['algo2_output_units'], index=[0]))
st.header("Transport decision")
st.dataframe(pd.DataFrame.from_dict(st.session_state['algo2_output_trans']))
st.header("DP")
st.header("Units decision")
st.dataframe(pd.DataFrame(st.session_state['algo3_output_units'], index=[0]))
st.header("Transport decision")
st.dataframe(pd.DataFrame.from_dict(st.session_state['algo3_output_trans']))
st.header("MIP")
st.header("Units decision")
st.dataframe(pd.DataFrame(st.session_state['algo4_output_units'], index=[0]))
st.header("Transport decision")
st.dataframe(pd.DataFrame.from_dict(st.session_state['algo4_output_trans']))
