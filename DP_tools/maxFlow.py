from ortools.graph import pywrapgraph
import numpy as np

INF = np.inf


def getCost(units, kitchensPicked, restaurantsPicked, restaurantsDemand, dist, cpd=1):
    # Define four parallel arrays: start_nodes, end_nodes, capacities, and unit costs
    # between each pair. For instance, the arc from node 0 to node 1 has a
    # capacity of 15 and a unit cost of 4.
    # indecies are [kitchensPicked|restaurantsPicked]
    start_nodes = []
    end_nodes = []
    capacities = [2 ** 31] * (len(kitchensPicked) * len(restaurantsPicked))  # inf
    unit_costs = []
    # have a path only between each kitchen and each restaurant
    for i in range(len(kitchensPicked)):
        for j in range(len(restaurantsPicked)):
            restIndex = len(kitchensPicked) + j
            start_nodes.append(i)
            end_nodes.append(restIndex)
            unit_costs.append(round(dist[kitchensPicked[i]][restaurantsPicked[j]] * 1000))
    # Define an array of supplies at each node.
    # kitchens have +ve supply
    supplies = [units[i]['capacity_kitchen'] for i in kitchensPicked]
    # restaurants have -ve supply
    supplies += [-int(restaurantsDemand[i]) for i in range(len(restaurantsPicked))]
    # Instantiate a SimpleMinCostFlow solver.
    min_cost_flow = pywrapgraph.SimpleMinCostFlow()
    # Add each arc.
    for i in range(0, len(start_nodes)):
        min_cost_flow.AddArcWithCapacityAndUnitCost(start_nodes[i], end_nodes[i], capacities[i], unit_costs[i])
    # Add node supplies.
    for i in range(0, len(supplies)):
        min_cost_flow.SetNodeSupply(i, supplies[i])
    # Find the minimum cost flow.
    if min_cost_flow.SolveMaxFlowWithMinCost() == min_cost_flow.OPTIMAL:
        totalCost = 0
        totalFlow = 0
        out = []
        for i in range(min_cost_flow.NumArcs()):
            if min_cost_flow.Flow(i) > 0:
                totalCost += (min_cost_flow.Flow(i) * cpd * dist[kitchensPicked[min_cost_flow.Tail(i)]][
                    restaurantsPicked[min_cost_flow.Head(i) - len(kitchensPicked)]])
                totalFlow += min_cost_flow.Flow(i)
                # from,to,amountTravelled
                out.append((
                    kitchensPicked[min_cost_flow.Tail(i)],
                    restaurantsPicked[min_cost_flow.Head(i) - len(kitchensPicked)],
                    min_cost_flow.Flow(i)))
        totalCost = (totalCost * 1)
        return totalFlow, totalCost, out
    else:
        return 0, INF, []
