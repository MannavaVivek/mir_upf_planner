from unified_planning.io import PDDLReader, PDDLWriter
from unified_planning.shortcuts import *
from unified_planning.engines import PlanGenerationResultStatus
import unified_planning as up

"""
This code contains the demo to 
1. parse a pddl problem file
2. remove the and goals from the problem and add it's children one by one
3. solve the problem using the oneshot planner
4. for every action in the plan, ask the user if the action was correct
5. if the action was correct, update the corresponding initial states
6. if the action was incorrect, remove the goal and replan for the next goal
"""

up.shortcuts.get_environment().credits_stream = None

reader = PDDLReader()
problem = reader.parse_problem("domain.pddl", "smaller_problem.pddl")

# removing the and goals from the problem and add it's children later
goals = []
for goal in problem.goals:
    if goal.is_and():
        for g in goal.args:
            goals.append(g)
    else:
        goals.append(goal)

problem.clear_goals()

removed_goals = [] # empty list to store the goals that were removed if action failed

# create a dictionary of fluents and objects to update the initial states
fluents_dict = {}
for fluent in problem.fluents:
    fluents_dict[str(fluent.name)] = problem.fluent(f"{fluent.name}")

objects_dict = {}
for obj in problem.all_objects:
    objects_dict[str(obj.name)] = problem.object(f"{obj.name}")

planner = OneshotPlanner(problem_kind=problem.kind, optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY)

previous_goal = None

for goal in goals:
    print('Solving for: ',goal)
    if previous_goal:
        problem.clear_goals() # TODO: this is a hack, need to fix this when having more goals. posted question on github
    problem.add_goal(goal)
    previous_goal = goal
    plan = planner.solve(problem).plan.actions
    for action in plan:
        user_input = input(f'\t{action}\twas the action correct? (y/n)')
        if not user_input or user_input == '' or user_input == ' ' :
            user_input = 'y'
        if user_input == 'y':
            action_name = action.action.name
            action_params = [str(params ) for params in action.actual_parameters]
            if action_name == "move_base": # TODO: need to organize this better
                problem.set_initial_value(fluents_dict['at'](objects_dict[action_params[0]], objects_dict[action_params[1]]), False)
                problem.set_initial_value(fluents_dict['at'](objects_dict[action_params[0]], objects_dict[action_params[2]]), True)
                problem.set_initial_value(fluents_dict['perceived'](objects_dict[action_params[1]]), False)
                problem.set_initial_value(fluents_dict['perceived'](objects_dict[action_params[2]]), False)
            elif action_name == "perceive":
                problem.set_initial_value(fluents_dict['perceived'](objects_dict[action_params[1]]), True)
            elif action_name == "pick":
                problem.set_initial_value(fluents_dict['on'](objects_dict[action_params[2]], objects_dict[action_params[1]]), False)
                problem.set_initial_value(fluents_dict['gripper_is_free'](objects_dict[action_params[0]]), False)
                problem.set_initial_value(fluents_dict['holding'](objects_dict[action_params[0]], objects_dict[action_params[2]]), True)
            elif action_name == "stage_general" or action_name == "stage_large":
                problem.set_initial_value(fluents_dict['holding'](objects_dict[action_params[0]], objects_dict[action_params[2]]), False)
                problem.set_initial_value(fluents_dict['gripper_is_free'](objects_dict[action_params[0]]), True)
                problem.set_initial_value(fluents_dict['stored'](objects_dict[action_params[2]], objects_dict[action_params[1]]), True)
                problem.set_initial_value(fluents_dict['occupied'](objects_dict[action_params[1]]), True)
            elif action_name == "unstage":
                problem.set_initial_value(fluents_dict['stored'](objects_dict[action_params[2]], objects_dict[action_params[1]]), False)
                problem.set_initial_value(fluents_dict['occupied'](objects_dict[action_params[1]]), False)
                problem.set_initial_value(fluents_dict['gripper_is_free'](objects_dict[action_params[0]]), False)
                problem.set_initial_value(fluents_dict['holding'](objects_dict[action_params[0]], objects_dict[action_params[2]]), True)
            elif action_name == "place":
                problem.set_initial_value(fluents_dict['holding'](objects_dict[action_params[0]], objects_dict[action_params[2]]), False)
                problem.set_initial_value(fluents_dict['gripper_is_free'](objects_dict[action_params[0]]), True)
                problem.set_initial_value(fluents_dict['on'](objects_dict[action_params[2]], objects_dict[action_params[1]]), True)
                problem.set_initial_value(fluents_dict['perceived'](objects_dict[action_params[1]]), False)
            elif action_name == "insert":
                problem.set_initial_value(fluents_dict['in'](objects_dict[action_params[3]], objects_dict[action_params[4]]), True)
                problem.set_initial_value(fluents_dict['on'](objects_dict[action_params[3]], objects_dict[action_params[2]]), True)
                problem.set_initial_value(fluents_dict['heavy'](objects_dict[action_params[3]]), True)
                problem.set_initial_value(fluents_dict['heavy'](objects_dict[action_params[4]]), True)
                problem.set_initial_value(fluents_dict['stored'](objects_dict[action_params[1]], objects_dict[action_params[3]]), False)
                problem.set_initial_value(fluents_dict['occupied'](objects_dict[action_params[1]]), False)
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