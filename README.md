# mir_upf_planner
Planner system developed for the b-it-bots @work team using UPF (Unified Planning Framework).

## Installation

To install the UPF framework, use the following command:

```bash
pip install unified-planning[engines]
```

## Files: 

Current progress is a mockup for planning that adds individual goals and verifies actions with user. 
If any action failed, that goal is removed and we continue. 
This is implemented using both the OneShot planner and the Replanner engine. 

The domain and problem file are  modified for use with UPF 