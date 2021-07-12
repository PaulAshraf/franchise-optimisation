from ortools.graph import pywrapgraph
import numpy as np
INF=np.inf
def getCost(units,kitchensPicked,restaurantsPicked,restaurantsDemand,dist,cpd=1):

    # Define four parallel arrays: start_nodes, end_nodes, capacities, and unit costs
    # between each pair. For instance, the arc from node 0 to node 1 has a
    # capacity of 15 and a unit cost of 4.
    
    #indecies are [kitchensPicked|restaurantsPicked]
    start_nodes = []
    end_nodes   = []
    capacities  = [2**31]*(len(kitchensPicked)*len(restaurantsPicked)) #inf
    unit_costs  = []
    #have a path only between each kitchen and each restaurant
    for i in range(len(kitchensPicked)):
        for j in range(len(restaurantsPicked)):
            restIndex=len(kitchensPicked)+j
            start_nodes.append(i)
            end_nodes.append(restIndex)
            unit_costs.append(round(dist[kitchensPicked[i]][restaurantsPicked[j]] * 1000 ))
    # s=[kitchensPicked[j] for j in start_nodes]
    # r=[restaurantsPicked[i-len(kitchensPicked)] for i in end_nodes]
    # print(list(zip(s,r,unit_costs)))


    # Define an array of supplies at each node.
    # kitchens have +ve supply
    supplies = [units[i]["capacity_kitchen"] for i in kitchensPicked]
    # restaurants have -ve supply
    supplies+= [-units[i]["capacity_restaurant"] for i in restaurantsPicked]
    # print(start_nodes)
    # print(end_nodes)
    # print(supplies)
    # Instantiate a SimpleMinCostFlow solver.
    min_cost_flow = pywrapgraph.SimpleMinCostFlow()

    # print(start_nodes,
    # end_nodes,
    # capacities,
    # unit_costs,
    # supplies)
    # Add each arc.
    for i in range(0, len(start_nodes)):
        min_cost_flow.AddArcWithCapacityAndUnitCost(start_nodes[i], end_nodes[i],
                                                capacities[i], unit_costs[i])

  # Add node supplies.
    for i in range(0, len(supplies)):
        min_cost_flow.SetNodeSupply(i, supplies[i])

  # Find the minimum cost flow.
    if min_cost_flow.SolveMaxFlowWithMinCost() == min_cost_flow.OPTIMAL:
        # print('')
        # print('  Arc    Flow / Capacity  Cost')
        totalCost=0
        totalFlow=0
        out=[]
        for i in range(min_cost_flow.NumArcs()):
            if min_cost_flow.Flow(i)>0:
                totalCost += (min_cost_flow.Flow(i) * cpd * \
                    dist[kitchensPicked[min_cost_flow.Tail(i)]][restaurantsPicked[min_cost_flow.Head(i)-len(kitchensPicked)]])
                totalFlow += min_cost_flow.Flow(i) 
                # totalCost += min_cost_flow.UnitCost(i) 
                #from,to,amountTravelled
                out.append((
                    kitchensPicked[min_cost_flow.Tail(i)],
                    restaurantsPicked[min_cost_flow.Head(i)-len(kitchensPicked)],
                    min_cost_flow.Flow(i)))
        totalCost = (totalCost*365)
        # print('Minimum cost:', totalCost)
            # print('%1s -> %1s   %3s  / %3s       %3s' % (
            #     min_cost_flow.Tail(i),
            #     min_cost_flow.Head(i),
            #     min_cost_flow.Flow(i),
            #     min_cost_flow.Capacity(i))
        return totalFlow,totalCost,out
    else:
        # print('There was an issue with the min cost flow input.')
        return 0,INF,[]