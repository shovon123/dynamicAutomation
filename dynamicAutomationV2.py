"""
Advantage
- user intervention is none
- can contradict automations
"""

import os
import pandas as pd

""" debug print including the dataframe """
def dfprint(str, shouldPrint = True):
    if shouldPrint:
        print(f"\n======= {str} =======\n{df.head(6).to_string()}")

""" debug print without the dataframe """
def comment(str, shouldPrint = True):
    if shouldPrint:
        print(f"\n======= {str} =======")

"""File Appending is being used, remove previous file to avoid duplicates"""
def clean_file():
    if os.path.exists("automation.csv"):
        os.remove("automation.csv")

    if os.path.exists("garbage.csv"):
        os.remove("garbage.csv")

""" 9:29AM --> 9AM, 9:30PM --> 10PM """
def round_time(time_str):
    hour, minute = str(time_str).split(":")

    new_minute = '00' + minute[2:]              #minute[2:0] --> AM/PM
    if int(minute[0]+minute[1]) < 30:
        new_time = f"{hour}:{new_minute}"
        return new_time

    else:
        new_hour = str(int(hour)+1)
        new_time = f"{new_hour}:{new_minute}"
        return new_time

"""
#(0) ORIGINAL       --> (1) NO LEADING & TRAILING spaces --> (2) NO USELESS columns -->
#(3) Rounded Time   --> (4) NO DUPLICATE rows
"""
def clean_df(df, shouldPrint):
    dfprint(f"({0}) ORIGINAL Data", shouldPrint)

    df.columns = df.columns.str.replace(' ', '')
    dfprint(f"({1}) Removed LEADING and TRAILING SPACE (Error Handling)", shouldPrint)

    df.drop(['deviceID', 'eventID'], axis=1, inplace=True)
    dfprint(f"({2}) Removed USELESS COLUMNS (IDs doesn't help find behaviors)", shouldPrint)

    df['time'] = df['time'].apply(lambda x: round_time(x))
    dfprint(f"({3}) ROUNDED the TIME (repetitive behavior happens in similar time)", shouldPrint)

    df.drop_duplicates(inplace=True)
    dfprint(f"({4}) removed DUPLICATE ROWS (to avoid the anomaly of receiving same data twice)", shouldPrint)

"""
#(5) update Date type (to retrieve DAY) --> (6) update value type (to add to behavior column) -->
#(7) No Update in Time column           --> (8) Sort by day (then time)
#(9) add 'day' column (from Date)       --> (10)add behavior column (concate other column)
"""
def modify_df(df, shouldPrint):
    oldDateType = df['date'].dtype
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    newDateType = df['date'].dtype
    dfprint(f"({5}) UPDATED TYPE of 'DATE' (to use datetime64 functions): {oldDateType} --> {newDateType}", shouldPrint)

    oldValueType = df['value'].dtype
    df['value'] = df['value'].astype('str')
    newValueType = df['value'].dtype
    dfprint(f"({6}) UPDATED TYPE of 'value' (to concatenate): {oldValueType} --> {newValueType}", shouldPrint)

    # ***** OBJECT DOES NOT PROPERLY SORT ITSELF *****
    oldDateType = df['time'].dtype
    df['time'] = pd.to_datetime(df['time'], format='%I:%M%p')   # XXX not '%I:%M %p' XXX
    newDateType = df['time'].dtype
    dfprint(f"({7}) UPDATED TYPE of 'Time' (to SORT): {oldDateType} --> {newDateType}", shouldPrint)

    df.sort_values(by=['date', 'time'], ascending=[True, True], inplace=True)
    dfprint(f"({8}) Sort by DATE and then by TIME (to observe behavior gradually)", shouldPrint)

    #TO VISUALIZE the time BETTER
    oldDateType = df['time'].dtype
    df['time'] = df['time'].dt.strftime('%I:%M %p')
    newDateType = df['time'].dtype
    dfprint(f"({9}) UPDATED TYPE of 'Time' (to SORT): {oldDateType} --> {newDateType}", shouldPrint)

    df.insert(2, 'day', df['date'].dt.day_name())
    dfprint(f"({10}) ADDED DAY column (to find weekly pattern)", shouldPrint)

    df['behavior'] = df['time'] + " " + df['day'] + " " + df['device'] + " " + df['action'] + " " + df['value']
    dfprint(f"({11}) ADDED BEHAVIOR column (the column to be observed as repetitive)", shouldPrint)

df = pd.read_csv("contradicting_behaviors.csv")
def main(shouldPrint):
    clean_file()
    clean_df(df, False)
    modify_df(df, False)

    #find out REPETITIVE PATTERN to be TRANSFORMED into AUTOMATION

    comment(f"({12}) Hold Confidence of each behavior & find each daily behavior", shouldPrint)

    behavior_confidences = {}
    comment(f"({13}) INITIALLY behavior_confidences (dict) = {behavior_confidences}", shouldPrint)

    day_behaviors = {"Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [],
                     "Friday": [], "Saturday": [], "Sunday": []}
    comment(f"({14}) INITIALLY day_behaviors = {day_behaviors}", shouldPrint)

    automations = []
    comment(f"({15}) INITIALLY automations (after meeting threshold) = {automations}", shouldPrint)

    comment(f"({16}) observe logs of repetitive behavior", shouldPrint)
    update_df_confidence(df, behavior_confidences, day_behaviors, automations)

    for str in automations:  print(f"{str}")  # DEBUG LOG FOR EVALUATION
    for str in behavior_confidences:  print(f"{str} --> {behavior_confidences[str]}")  # DEBUG LOG FOR EVALUATION


"""
Check each day to figure out every weekly behavior and update their confidence
- if the behavior didn't exist before
    - add the behavior as key and give a initial confidence as value in the `behavior_confidences` dictionary
    - add the behavior in `day_behaviors` to observe them each week
- increase confidence if the behavior is occurring weekly
- decrease confidence if the behavior is absent weekly (after occurring at least once)

*** NEED TO ADJUST THE CONFIDENCE MANUALLY and see what works best ***
- alpha = the exponential smoothing factor used when increasing confidence
- beta  = the exponential smoothing factor used when decreasing confidence
- base_confidence = the base confidence given for new behavior
- NO NEED TO adjust threshold since alpha, beta will cross them based on proper input
"""

alpha = 0.3; decay=0.3; base_confidence = 80
def update_df_confidence(df, behavior_confidences, day_behaviors, automations):
    comment(f"({17}) Manually Input alpha, beta, base_confidence (look description above this function)")
    global alpha, decay, base_confidence
    """
    alpha = float(input("alpha [0.0-1.0] = "))
    decay = float(input("decay [0.0-1.0] = "))
    base_confidence = int(input("base confidence [0-100] = "))
    """

    oldDate = None; current_day = None; pending_tasks = []

    # Check EACH day
    for i in df.index:
        print(f"$$$$$$$$$$$$$$$$$$$$$$$$ SHOVON : {i} $$$$$$$$$$$$$$$$$$$$$$$$")
        # When NEW DATE is found
        if oldDate is None or oldDate != df.loc[i, 'date']:
            # DECREASE CONFIDENCE if some behaviors did not occur from PREVIOUS DATE
            if pending_tasks:
                for task in pending_tasks:
                    decrease_confidence(behavior_confidences, task, automations, day_behaviors[current_day])

            #update date and task to DIFFERENTIATE Date and observe PREVIOUS DAY TASK Which were absent
            oldDate = df.loc[i, 'date']; current_day = df.loc[i, 'day']
            pending_tasks = day_behaviors[current_day].copy()
            print(f" =======>>> date: {oldDate}, day: {current_day}, pending: {pending_tasks}")

        #if a behavior exists, return it's last confidence OR IF NOT, return behavior_does_not_exist
        behavior = behavior_confidences.get(df.loc[i, 'behavior'], 'behavior_does_not_exist')

        print(f"##>>-- date: {df.loc[i, 'date']} behavior: {df.loc[i, 'behavior']}, automations: {automations} --<<## ")
        if df.loc[i, 'behavior'] in automations:
            print(f">>>>>>>>>>>>>>>>>>>> behavior: {df.loc[i, 'behavior']} is in AUTOMATIONS <<<<<<<<<<<<<<<<<<<<")
            continue

        if behavior == 'behavior_does_not_exist':
            behavior_confidences[df.loc[i, 'behavior']] = [base_confidence]
            # append the behavior in weekly pattern
            day_behaviors[current_day] += [df.loc[i, 'behavior']]

            #>>> HIGHLY UNLIKELY. BUT WHAT IF DEVELOPER WANTS IT TO BE REPETITIVE FROM DAY 1 <<<
            if base_confidence > 75:
                if not isContradictingBehavior(i, df, automations):
                    # add in automations since they are not contradicting
                    automations.append(df.loc[i, 'behavior'])       # XXX not behavior, since it did not exist XXX
                    append_in_automation_csv(i, df) # XXX not behavior, since it did not exist XXX
                else:
                    print("INITIAL CONTRADICTION")

        else:
            #increase existing behavior's confidence since it occurred this week
            increase_confidence(i, df, behavior_confidences, automations)
            #since the behavior occurred this week, remove it from this week's pending_tasks
            if df.loc[i, 'behavior'] in pending_tasks:
                pending_tasks.remove(df.loc[i, 'behavior'])

    #Final Day's Pending tasks (This won't be necessary since there are no final day in real time)
    if pending_tasks:
        for task in pending_tasks:
            # @@ day_behaviors[current_day] is passed by reference. so any modification affects the main column @@
            decrease_confidence(behavior_confidences, task, automations, day_behaviors[current_day])

"""
- find the existing behavior from dictionary and append the new score found using Exponential Smoothing Formula
- if the score exceeds the threshold, extract that behavior for the user to use as automation.
"""
def increase_confidence(i, df, dict_for_behavior_confidences, automations):
    behavior = df.loc[i, 'behavior']
    specific_behavior_confidence_list = dict_for_behavior_confidences[behavior]
    last_confidence = specific_behavior_confidence_list[-1]

    event = 1 * 100  # since behavior occurred * percentage
    new_confidence = alpha * 100 + (1 - alpha) * last_confidence    # EXPONENTIAL SMOOTHING FORMULA


    if new_confidence > 75:
        if not isContradictingBehavior(i, df, automations):
            # add in automations since they are not contradicting
            automations.append(behavior)
            append_in_automation_csv(i, df)
            return


    #appending new confidence for the behavior to PLOT them later
    dict_for_behavior_confidences[behavior].append(new_confidence)

def isContradictingBehavior(i, df, automations):
    print(f"\n\n")
    row =  df.loc[i]
    print(F"observing row is :\n{row}")
    print(f"\nobserving behavior: {row['behavior']}")
    contradictory_behavior = ""

    if row['action'] == 'power':
        print("POWER ACTION")
        if row['value'] == '0':
            contradictory_behavior = row['time'] + " " + row['day'] + " " + row['device'] + " " + row['action'] + " " + "1"
        else:
            contradictory_behavior = row['time'] + " " + row['day'] + " " + row['device'] + " " + row['action'] + " " + "0"

    print(f"observing contradictory behavior: {contradictory_behavior}\n")

    if contradictory_behavior in automations:
        print("CONTRADICTION EXISTS")
        automations.remove(contradictory_behavior)
        remove_from_automation_csv(contradictory_behavior)

        print(f"AUTOMATIONS PUT IN GARBAGE FROM CONTRADICTION: {contradictory_behavior}")
        append_in_garbage_csv(contradictory_behavior)
        return True

    else:
        print("NO CONTRADICTORY BEHAVIOR. CAN APPEND IN AUTOMATION")
        return False

    if row['action'] == 'power':
        print("OTHER ACTION")

    print(f"\n\n")

"""
- automation file already exists since I am removing a behavior from it
- figure out which row the behavior exists and delete it
"""
def remove_from_automation_csv(behavior_description):
    print(f"REMOVING FROM AUTOMATION: {behavior_description}")
    automation_df = pd.read_csv("automation.csv")

    #find the index where the behavior exists and drop them
    index_to_delete = automation_df[automation_df['behavior'] == behavior_description].index
    automation_df.drop(index_to_delete, inplace=True)

    #over-write previous file without the new index
    automation_df.to_csv('automation.csv', header=False, index=False)

"""
- if the repetitive file does not exist, create one and append the behavior
"""
def append_in_automation_csv(i, old_df):
    try:
        behavior_description = old_df.loc[i, 'behavior']
        automation_df = pd.read_csv("automation.csv")

        # *** *** *** IF A FILE EXISTS WITH NO HEADER --> pd.errors.EmptyDataError *** *** ***
        if len(automation_df) == 0:
            print("AUTOMATION CSV FILE IS EMPTY BUT IT HAS HEADERS")
            df = pd.DataFrame(columns=["behavior"])
            df.to_csv('automation.csv', index=False)

        new_row_data = {"behavior": [behavior_description]}
        new_row_df = pd.DataFrame(new_row_data)
        new_row_df.to_csv('automation.csv', mode='a', header=False, index=False)

    except FileNotFoundError:
        print("AUTOMATION File does not exist, create a empty file with one column name")

        df = pd.DataFrame(columns=["behavior", "confidence"])
        df.to_csv('automation.csv', index=False)

        append_in_automation_csv(i, old_df)

    #***** DID NOT RAISE THIS EXCEPTION (FILE MAY EXIST BUT IT HAS NO HEADERS) *******
    except pd.errors.EmptyDataError:
        print("AUTOMATION File EXISTS BUT IT HAS NO HEADER, create a empty file with one column name")

        df = pd.DataFrame(columns=["behavior", "confidence"])
        df.to_csv('automation.csv', index=False)

        append_in_automation_csv(i, old_df)
"""
- find the existing behavior from dictionary and append the new score found using Exponential Smoothing Formula
- if the score exceeds the threshold, REMOVE that behavior since it is not repetitive anymore.
- keep track of every dumped behavior in garbage
"""
def decrease_confidence(dict_for_behavior_confidences, behavior, automations, daily_behaviors):
    specific_behavior_confidence_list = dict_for_behavior_confidences[behavior]
    last_confidence = specific_behavior_confidence_list[-1]

    event = 0 * 100   #since behavior did not occur * percentage
    new_confidence = decay * event + (1 - decay) * last_confidence    # EXPONENTIAL SMOOTHING FORMULA

    if new_confidence < 35:
        if behavior in dict_for_behavior_confidences:
            dict_for_behavior_confidences[behavior].append(new_confidence)
            # Remove from behavior dictionary since it is not repetitive
            print(f"behavior to be DROPPED: {behavior}, PAST: {dict_for_behavior_confidences.pop(behavior, None)}")
            # Remove from daily behaviors to not check it when checking pending behaviors
            daily_behaviors.remove(behavior)
            # keep track of every discarded behavior as NOT REPETITIVE
            append_in_garbage_csv(behavior)
            return

    #decrease the behavior (if it does not decrease below the threshold)
    dict_for_behavior_confidences[behavior].append(new_confidence)

"""
- add the discarded behavior in garbage file (if it exist, create one if it doesn't
"""
def append_in_garbage_csv(behavior_description):
    try:
        repetitive_df = pd.read_csv("garbage.csv")
        new_row_data = {"behavior": [behavior_description]}
        new_row_df = pd.DataFrame(new_row_data)
        new_row_df.to_csv('garbage.csv', mode='a', header=False, index=False)

    except FileNotFoundError:
        print("GARBAGE File does not exist, create a empty file with one column name")
        df = pd.DataFrame(columns=['behavior'])
        df.to_csv('garbage.csv', index=False)

        append_in_garbage_csv(behavior_description)

main(False)