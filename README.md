# Summary
- the proposed method will look into real-time data and figure out the repetitive behavior to be registered as automation
- Automation is set when they reach a certain threshold and will only be updated if they are either contradicted or merged with other behavior 

# background
- Now-a-days IoT device are controlled through an app. but as the number of device rises, maintaining them manually becomes difficult
- there is a feature named automation which takes in conditions (Time, Button, Stats) and based on the condition, changes the status of some other devices
- registering an automation is difficult. maintaining them becomes even more difficult. which is why we are proposing the above method

# input
## behavior.csv
- getting real-time data is difficult since we are observing weekly-monthly data. so we will be mimicking them by checking each row of the behavior.csv instead.
### automation.csv
- we will be creating and updating automation.csv based on repetitive behavior and also maintain it

# algorithm
## Re-inforcement Learning
- if a repetitive behavior occurs, we are rewarding the behavior through exponential smoothing. and if the reward reaches a certain threshold, we are updating policy
- policy adaptation is done in this proposal
