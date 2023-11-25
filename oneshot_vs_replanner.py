from unified_planning.io import PDDLReader, PDDLWriter
from unified_planning.shortcuts import *
from unified_planning.engines import PlanGenerationResultStatus
import unified_planning as up
import re

"""
This script compares the performance of the oneshot planner and the replanner
for the same problem and domain file. 
"""

up.shortcuts.get_environment().credits_stream = None

pattern = r"(\w+)\(([^)]+)\)"
def parse_action(string):
    """
    Takes in plan action string and returns the action name and parameters
    """
    match = re.match(pattern, string)
    if match:
        key = match.group(1)
        params = match.group(2).split(", ")
        return key, params

reader = PDDLReader()
problem = reader.parse_problem("domain.pddl", "smaller_problem.pddl")

# removing the and goals from the problem and add it's children
goals = []
for goal in problem.goals:
    if goal.is_and():
        for g in goal.args:
            goals.append(g)
    else:
        goals.append(goal)

problem.clear_goals()

removed_goals = []
succeeded_goals = []



previous_goal = None
for goal in goals:
    print('Solving for: ',goal)
    problem.add_goal(goal)

print("Using oneshot planner")
planner = OneshotPlanner(problem_kind=problem.kind, optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY)
plan = planner.solve(problem).plan
print(plan)

print("Using replanner")
replanner = Replanner(problem, name='replanner[fast-downward]', optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY)
plan = replanner.resolve().plan
print(plan)