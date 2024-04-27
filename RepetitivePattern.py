import os
import pandas as pd

""" debug print including the dataframe """
def dfprint(str):   print(f"\n======= {str} =======\n{df.head(4).to_string()}")

""" debug print without the dataframe """
def comment(str):   print(f"\n======= {str} =======")

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
def clean_df(df):
    dfprint(f"({0}) ORIGINAL Data")

    df.columns = df.columns.str.replace(' ', '')
    dfprint(f"({1}) Removed LEADING and TRAILING SPACE (Error Handling)")

    df.drop(['deviceID', 'eventID'], axis=1, inplace=True)
    dfprint(f"({2}) Removed USELESS COLUMNS (IDs doesn't help find behaviors)")

    df['time'] = df['time'].apply(lambda x: round_time(x))
    dfprint(f"({3}) ROUNDED the TIME (repetitive behavior happens in similar time)")

    df.drop_duplicates(inplace=True)
    dfprint(f"({4}) removed DUPLICATE ROWS (to avoid the anomaly of receiving same data twice)")

"""
#(5) update Date type (to retrieve DAY) --> (6) update value type (to add to behavior column) -->
#(7) No Update in Time column           --> (8) Sort by day (then time)
#(9) add 'day' column (from Date)       --> (10)add behavior column (concate other column)
"""
def modify_df(df):
    oldDateType = df['date'].dtype
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    newDateType = df['date'].dtype
    dfprint(f"({5}) UPDATED TYPE of 'DATE' (to use datetime64 functions): {oldDateType} --> {newDateType}")

    oldValueType = df['value'].dtype
    df['value'] = df['value'].astype('str')
    newValueType = df['value'].dtype
    dfprint(f"({6}) UPDATED TYPE of 'value' (to concatenate): {oldValueType} --> {newValueType}")


    comment(f"({7}) 'TIME' functions are NOT needed. so it is kept as object")

    df.sort_values(by=['date', 'time'], ascending=[True, True], inplace=True)
    dfprint(f"({8}) Sort by DATE and then by TIME (to observe behavior gradually)")

    df.insert(2, 'day', df['date'].dt.day_name())
    dfprint(f"({9}) ADDED DAY column (to find weekly pattern)")

    df['behavior'] = df['time'] + " " + df['day'] + " " + df['device'] + " " + df['action'] + " " + df['value']
    dfprint(f"({10}) ADDED BEHAVIOR column (the column to be observed as repetitive)")

"""File Appending is being used, remove previous file to avoid duplicates"""
def clean_file():
    if os.path.exists("automation.csv"):
        os.remove("automation.csv")

    if os.path.exists("garbage.csv"):
        os.remove("garbage.csv")

df = pd.read_csv("behavior.csv")
def main():
    if os.path.exists("repetitive.csv"):
        os.remove("repetitive.csv")

    clean_file()
    clean_df(df)
    modify_df(df)

    #find out REPETITIVE PATTERN to be TRANSFORMED into AUTOMATION

    comment(f"({11}) Hold Confidence of each behavior & find each daily behavior")

    behavior_confidences = {}
    comment(f"({12}) INITIALLY behavior_confidences (dict) = {behavior_confidences}")

    day_behaviors = {"Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [],
                     "Friday": [], "Saturday": [], "Sunday": []}
    comment(f"({13}) INITIALLY day_behaviors = {day_behaviors}")

    repetitive_pattern = []
    comment(f"({14}) INITIALLY repetitive_pattern (after meeting threshold) = {repetitive_pattern}")

    comment(f"({15}) observe logs of repetitive behavior")
    update_df_confidence(df, behavior_confidences, day_behaviors, repetitive_pattern)
    for str in repetitive_pattern:  print(f"{str} --> {behavior_confidences[str]}")  # DEBUG LOG FOR EVALUATION

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

alpha = 0.0; decay=0.0; base_confidence = 0
def update_df_confidence(df, behavior_confidences, day_behaviors, repetitive_pattern):
    comment(f"({16}) Manually Input alpha, beta, base_confidence (look description above this function)")
    global alpha, decay, base_confidence
    alpha = float(input("alpha [0.0-1.0] = "))
    decay = float(input("decay [0.0-1.0] = "))
    base_confidence = int(input("base confidence [0-100] = "))

    oldDate = None; current_day = None; pending_tasks = []

    # Check EACH day
    for i in df.index:
        # When NEW DATE is found
        if oldDate is None or oldDate != df.loc[i, 'date']:
            # DECREASE CONFIDENCE if some behaviors did not occur from PREVIOUS DATE
            if pending_tasks:
                for task in pending_tasks:
                    decrease_confidence(behavior_confidences, task, repetitive_pattern, day_behaviors[current_day])

            #update date and task to DIFFERENTIATE Date and observe PREVIOUS DAY TASK Which were absent
            oldDate = df.loc[i, 'date']; current_day = df.loc[i, 'day']
            pending_tasks = day_behaviors[current_day].copy()
            print(f" =======>>> date: {oldDate}, day: {current_day}, pending: {pending_tasks}")

        #if a behavior exists, return it's last confidence OR IF NOT, return behavior_does_not_exist
        behavior = behavior_confidences.get(df.loc[i, 'behavior'], 'behavior_does_not_exist')

        if behavior == 'behavior_does_not_exist':
            behavior_confidences[df.loc[i, 'behavior']] = [base_confidence]
            # append the behavior in weekly pattern
            day_behaviors[current_day] += [df.loc[i, 'behavior']]

        else:
            #increase existing behavior's confidence since it occurred this week
            increase_confidence(behavior_confidences, df.loc[i, 'behavior'], repetitive_pattern)

            #since the behavior occurred this week, remove it from this week's pending_tasks
            if df.loc[i, 'behavior'] in pending_tasks:
                pending_tasks.remove(df.loc[i, 'behavior'])

    #Final Day's Pending tasks (This won't be necessary since there are no final day in real time)
    if pending_tasks:
        for task in pending_tasks:
            # @@ day_behaviors[current_day] is passed by reference. so any modification affects the main column @@
            decrease_confidence(behavior_confidences, task, repetitive_pattern, day_behaviors[current_day])

"""
- find the existing behavior from dictionary and append the new score found using Exponential Smoothing Formula
- if the score exceeds the threshold, extract that behavior for the user to use as automation.
"""
def increase_confidence(dict_for_behavior_confidences, behavior, repetitive_pattern):
    specific_behavior_confidence_list = dict_for_behavior_confidences[behavior]
    last_confidence = specific_behavior_confidence_list[-1]

    event = 1 * 100  # since behavior occurred * percentage
    new_confidence = alpha * 100 + (1 - alpha) * last_confidence    # EXPONENTIAL SMOOTHING FORMULA

    if new_confidence > 75:
        if behavior in repetitive_pattern:
            pass                                    # nothing to append since it is already there
        else:
            # add in repetitive pattern
            repetitive_pattern.append(behavior)
            append_in_repetitive_csv(behavior)

    #appending new confidence for the behavior to PLOT them later
    dict_for_behavior_confidences[behavior].append(new_confidence)

"""
- if the repetitive file does not exist, create one and append the behavior
"""
def append_in_repetitive_csv(behavior_description):
    try:
        repetitive_df = pd.read_csv("repetitive.csv")

        new_row_data = {"behavior": [behavior_description]}
        new_row_df = pd.DataFrame(new_row_data)

        new_row_df.to_csv('repetitive.csv', mode='a', header=False, index=False)

    except FileNotFoundError:
        print("REPETITIVE File does not exist, create a empty file with one column name")
        df = pd.DataFrame(columns=["behavior", "confidence"])
        df.to_csv('repetitive.csv', index=False)

        append_in_repetitive_csv(behavior_description)

"""
- find the existing behavior from dictionary and append the new score found using Exponential Smoothing Formula
- if the score exceeds the threshold, REMOVE that behavior since it is not repetitive anymore.
- keep track of every dumped behavior in garbage
"""
def decrease_confidence(dict_for_behavior_confidences, behavior, repetitive_pattern, daily_behaviors):
    print(f"SHOVON HERE FOR: {behavior} with: {dict_for_behavior_confidences[behavior]}")
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

            # Remove from repetitive_pattern since it is not repetitive
            if behavior in repetitive_pattern:
                repetitive_pattern.remove(behavior)
                remove_from_repetitive_csv(behavior)

                print(f"A REPETITIVE BEHAVIOR PUT IN GARBAGE: {behavior}")
                append_in_garbage_csv(behavior)
                return

            else:
                return

    #decrease the behavior (if it does not decrease below the threshold)
    dict_for_behavior_confidences[behavior].append(new_confidence)

"""
- repetitive file already exists since I am removing a behavior from it
- figure out which row the behavior exists and delete it
"""
def remove_from_repetitive_csv(behavior_description):
    repetitive_df = pd.read_csv("repetitive.csv")

    #find the index where the behavior exists and drop them
    index_to_delete = repetitive_df[repetitive_df['behavior'] == behavior_description].index
    repetitive_df.drop(index_to_delete, inplace=True)

    #over-write previous file without the new index
    repetitive_df.to_csv('repetitive.csv', mode='a', header=False, index=False)

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

main()