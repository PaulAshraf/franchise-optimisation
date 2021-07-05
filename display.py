from utils import plot_solution
from solver import mip
from generate_data import generate_data, plot_units
import streamlit as st
import matplotlib.pyplot as plt
from functools import partial


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


def solve(solver):
    if solver == 'mip':
        solution = mip(st.session_state['units'], st.session_state['areas_demand'], radius=radius, budget=4e6, cpd=1, r=5)
        fig = plot_solution(solution, st.session_state['units'], st.session_state['areas_demand'])
        st.session_state['fig'] = fig


if 'units' not in st.session_state:
    units, areas_demand = generate_data()
    st.session_state['units'] = units
    st.session_state['areas_demand'] = areas_demand
    st.session_state['fig'] = plt.figure()

st.set_page_config(layout="wide")
st.set_option('deprecation.showPyplotGlobalUse', False)
left, right = st.beta_columns(2)

with left:
    st.header('Customise Random Data Ranges')
    sparcity = st.slider('Sparcity', 0, 100, 15)
    radius = st.slider('Radius', 0, 100, 10)
    num_units_per_area = st.slider('Number of units per area range', 0, 20, (2, 3))
    areas = st.slider('Areas', 0, 10, 6)
    demand_range = st.slider('Demand Range', 0, int(1e9), (int(1e8), int(1e9)), step=10000)
    rent_range = st.slider('Rent Range', 0, 20000, (3000, 15000), step=10)
    capacity_kitchen_range = st.slider('Kitchen Capacity Range', 0, 20000, (2000, 3000), step=10)
    capacity_restaurant_range = st.slider('Restaurant Capacity Range', 0, 1000, (300, 400), step=10)
    initial_kitchen_range = st.slider('Kitchen Initial Cost Range', 0, 2000000, (500000, 1000000), step=10000)
    initial_restaurant_range = st.slider('Restaurant Initial Cost Range', 0, 1000000, (100000, 200000), step=10000)

with right:
    st.button('Solve w/ MIP', on_click=partial(solve, 'mip'))
    st.button('Generate Data', on_click=get_units)
    st.pyplot(st.session_state['fig'], clear_figure=True)
