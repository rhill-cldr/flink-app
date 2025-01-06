# TODO: Optimization Logic Review Procedure

## Overview
This document outlines the procedure for reviewing the optimization logic implemented in the `src/server_optimizer.py` file. The optimization logic uses Google OR-Tools to determine the minimal server allocation that meets the required CPU and RAM while minimizing the total cost.

## Steps to Review Optimization Logic

### Step 1: Understand the Input Requirements
- [x] **Required CPU**: Total number of CPU cores required.
- [x] **Required RAM**: Total amount of RAM required in GB.

### Step 2: Examine the Server Data
- [x] The server data is loaded from `library/equinix.json`.
- [x] Each server type has a `server_type`, `price_hr`, and `hardware` details including `cpu`, `ram`, `storage`, `network`, and `graphics`.

### Step 3: Review the Optimization Model
- [x] **Solver Creation**: The optimization model is created using the SCIP backend of Google OR-Tools.
- [x] **Decision Variables**: The number of each server type to use is defined as decision variables.
- [x] **Constraints**:
  - [x] Total CPU constraint with redundancy factor.
  - [x] Total RAM constraint with redundancy factor.
- [x] **Objective**: Minimize the total cost of the server allocation.

### Step 4: Validate the Constraints
- [x] Ensure that the constraints correctly reflect the requirements and redundancy factor.
- [x] Verify that the constraints are correctly formulated to account for the number of CPUs and RAM in each server type.

### Step 5: Check the Objective Function
- [x] Verify that the objective function correctly calculates the total cost based on the number of servers of each type and their hourly price.

### Step 6: Review the Solution Handling
- [x] Check how the solution is handled after solving the optimization model.
- [x] Ensure that the solution values are correctly extracted and formatted for the output.

### Step 7: Test the Optimization Logic
- [x] Run the `src/server_optimizer.py` script with different input values to ensure it behaves as expected.
- [x] Validate the output against manually calculated results to ensure accuracy.

### Step 8: Document Any Changes or Findings
- [x] Document any changes made to the optimization logic during the review.
- [x] Note any findings or issues discovered during the review process.

## Example Usage
- [x] To test the optimization logic, run the following command:
```bash
python src/server_optimizer.py
```
This will execute the script with example cluster sizing requirements and print the optimization result.
