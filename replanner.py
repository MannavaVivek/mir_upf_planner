from unified_planning.io import PDDLReader, PDDLWriter
from unified_planning.shortcuts import *
from unified_planning.engines import PlanGenerationResultStatus
import unified_planning as up
import re

"""
This code contains the demo to 
1. parse a pddl problem file
2. remove the and goals from the problem and add it's children one by one
3. solve the problem using the replanner
4. for every action in the plan, ask the user if the action was correct
5. if the action was correct, update the corresponding initial states
6. if the action was incorrect, remove the goal and replan for the next goal
"""

# BUG: the replanner is not able to solve the problem as optimally as the oneshot planner. github q&a required

up.shortcuts.get_environment().credits_stream = None

# parsing the action string as an alternative to using the action name and parameters
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

# create a dictionary of fluents and objects to update the initial states
fluents_dict = {}
for fluent in problem.fluents:
    fluents_dict[str(fluent.name)] = problem.fluent(f"{fluent.name}")

objects_dict = {}
for obj in problem.all_objects:
    objects_dict[str(obj.name)] = problem.object(f"{obj.name}")

replanner = Replanner(problem, name='replanner[fast-downward]')

previous_goal = None
for goal in goals:
    print('Solving for: ',goal)
    replanner.add_goal(goal)
    if previous_goal:
        replanner.remove_goal(previous_goal)
    previous_goal = goal
    plan = replanner.resolve().plan.actions
    plan = [str(action) for action in plan]
    for action in plan:
        user_input = input(f'\t{action}\twas the action correct? (y/n)')
        if not user_input or user_input == '' or user_input == ' ' :
            user_input = 'y'
        if user_input == 'y':
            action_name, action_params = parse_action(action)
            if action_name == "move_base": # TODO: need to organize this better
                replanner.update_initial_value(fluents_dict['at'](objects_dict[action_params[0]], objects_dict[action_params[1]]), False)
                replanner.update_initial_value(fluents_dict['at'](objects_dict[action_params[0]], objects_dict[action_params[2]]), True)
                replanner.update_initial_value(fluents_dict['perceived'](objects_dict[action_params[1]]), False)
                replanner.update_initial_value(fluents_dict['perceived'](objects_dict[action_params[2]]), False)
            elif action_name == "perceive":
                replanner.update_initial_value(fluents_dict['perceived'](objects_dict[action_params[1]]), True)
            elif action_name == "pick":
                replanner.update_initial_value(fluents_dict['on'](objects_dict[action_params[2]], objects_dict[action_params[1]]), False)
                replanner.update_initial_value(fluents_dict['gripper_is_free'](objects_dict[action_params[0]]), False)
                replanner.update_initial_value(fluents_dict['holding'](objects_dict[action_params[0]], objects_dict[action_params[2]]), True)
            elif action_name == "stage_general" or action_name == "stage_large":
                replanner.update_initial_value(fluents_dict['holding'](objects_dict[action_params[0]], objects_dict[action_params[2]]), False)
                replanner.update_initial_value(fluents_dict['gripper_is_free'](objects_dict[action_params[0]]), True)
                replanner.update_initial_value(fluents_dict['stored'](objects_dict[action_params[2]], objects_dict[action_params[1]]), True)
                replanner.update_initial_value(fluents_dict['occupied'](objects_dict[action_params[1]]), True)
            elif action_name == "unstage":
                replanner.update_initial_value(fluents_dict['stored'](objects_dict[action_params[2]], objects_dict[action_params[1]]), False)
                replanner.update_initial_value(fluents_dict['occupied'](objects_dict[action_params[1]]), False)
                replanner.update_initial_value(fluents_dict['gripper_is_free'](objects_dict[action_params[0]]), False)
                replanner.update_initial_value(fluents_dict['holding'](objects_dict[action_params[0]], objects_dict[action_params[2]]), True)
            elif action_name == "place":
                replanner.update_initial_value(fluents_dict['holding'](objects_dict[action_params[0]], objects_dict[action_params[2]]), False)
                replanner.update_initial_value(fluents_dict['gripper_is_free'](objects_dict[action_params[0]]), True)
                replanner.update_initial_value(fluents_dict['on'](objects_dict[action_params[2]], objects_dict[action_params[1]]), True)
                replanner.update_initial_value(fluents_dict['perceived'](objects_dict[action_params[1]]), False)
            elif action_name == "insert":
                replanner.update_initial_value(fluents_dict['in'](objects_dict[action_params[3]], objects_dict[action_params[4]]), True)
                replanner.update_initial_value(fluents_dict['on'](objects_dict[action_params[3]], objects_dict[action_params[2]]), True)
                replanner.update_initial_value(fluents_dict['heavy'](objects_dict[action_params[3]]), True)
                replanner.update_initial_value(fluents_dict['heavy'](objects_dict[action_params[4]]), True)
                replanner.update_initial_value(fluents_dict['stored'](objects_dict[action_params[1]], objects_dict[action_params[3]]), False)
                replanner.update_initial_value(fluents_dict['occupied'](objects_dict[action_params[1]]), False)
        if user_input == 'n':
            if action_name == "pick":
                # TODO: need to deal with the pick specific cases
                print('pickf failed')
            elif action_name == "perceive":
                # TODO: need to deal with the pick specific cases here too
                print('perceive failed')
            elif action_name == "move_base":
                print('move_base failed')
            elif action_name == "stage_general" or action_name == "stage_large":
                print('stage failed')
            elif action_name == "unstage":
                print('unstage failed')
            elif action_name == "place":
                print('place failed')
            elif action_name == "insert":
                print('insert failed')
            else:
                print('action not recognized')

            removed_goals.append(goal)
            break

        # if no, remove the goal and continue
        # if yes, update the initial state and continue
