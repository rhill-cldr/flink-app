from ortools.linear_solver import pywraplp
import json
from typing import List, Dict

# Load server data
with open('library/equinix.json', 'r') as f:
    server_data = json.load(f)

def optimize_server_allocation(required_cpu: int, required_ram: int, redundancy_factor: float = 1.2) -> Dict:
    """Optimize server allocation to meet cluster sizing requirements while minimizing cost."""
    
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")

    if not solver:
        print("Solver not available.")
        return {}

    # Decision variables: number of each server type to use
    num_servers = {}
    for server in server_data:
        server_type = server["server_type"]
        num_servers[server_type] = solver.IntVar(0, solver.infinity(), f'num_servers_{server_type}')
        print(f"Decision variable for {server_type}: {num_servers[server_type]}")

    # Constraints
    # Total CPU constraint with redundancy factor
    total_cpu_constraint = sum(num_servers[server["server_type"]] * int(server["hardware"]["cpu_qty"]) for server in server_data)
    solver.Add(total_cpu_constraint >= required_cpu * redundancy_factor)
    print(f"Total CPU constraint: {total_cpu_constraint} >= {required_cpu * redundancy_factor}")

    # Total RAM constraint with redundancy factor
    total_ram_constraint = sum(num_servers[server["server_type"]] * int(server["hardware"]["ram"].split('GB')[0]) for server in server_data)
    solver.Add(total_ram_constraint >= required_ram * redundancy_factor)
    print(f"Total RAM constraint: {total_ram_constraint} >= {required_ram * redundancy_factor}")

    # Objective: minimize the total cost
    solver.Minimize(sum(num_servers[server["server_type"]] * server["price_hr"] for server in server_data))
    print("Objective function set to minimize total cost.")

    print(f"Solving with {solver.SolverVersion()}")
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print("Optimal solution found.")
        total_cost = solver.Objective().Value()
        print(f"Total cost: ${total_cost} per hour")
        server_allocation = {server["server_type"]: num_servers[server["server_type"]].solution_value() for server in server_data}
        print(f"Server allocation: {server_allocation}")
        result = {
            "total_cost": total_cost,
            "server_allocation": server_allocation
        }
        return result
    else:
        print("The problem does not have an optimal solution.")
        return {}

if __name__ == "__main__":
    # Example cluster sizing requirements (these should be dynamically loaded from your Flink jobs and services)
    required_cpu = 100  # Total required CPU cores
    required_ram = 1024  # Total required RAM in GB

    redundancy_factor = 1.2  # Example redundancy factor
    result = optimize_server_allocation(required_cpu, required_ram, redundancy_factor)
    print(result)
