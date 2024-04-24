"""
- READ DATA
- REMOVE DUPLICATE DATA  (TO AVOID ANOMALY WHEN IT RECEIVES SAME LOG TWICE)
- CONVERT DATA COLUMN TYPE (OBJECT --> DATETIME)
- SORT BY DATE, TIME (TO AVOID ANOMALY AND CHECK BEHAVIOR SEQUENTIALLY)
- ADD A DAY COLUMN TO FIGURE OUT EACH DAY'S BEHAVIOR
- ADD A BEHAVIOR COLUMN MERGING ALL THE OTHER COLUMN
- A BEHAVIOR DICTIONARY HOLDING CONFIDENCE OF EACH EXISTING BEHAVIOR
- CHECK EACH ROW OF LOG AND FIGURE OUT IF THE BEHAVIOR IS NEW
    - IF IT IS NEW, SET INITIAL CONFIDENCE (EX: 50)
    - IF OLD, INCREASE CONFIDENCE (ALPHA = 0.3, EVENT = 100) THROUGH SMOOTH EXPONENTIAL FORMULA

WHAT THIS IMPLEMENTATION LACKS
- DECREASING CONFIDENCE IN ABSENCE OF A EXISTING BEHAVIOR (PRE-DEFENSE #3)
- ROUND UP TIME (PRE-DEFENSE #4)
- THRESHOLD NOT ADDED (>75) TO PREDICT IF IT IS REPETITIVE. (PRE-DEFENSE #5)
"""
import pandas as pd

def round_time(time_str):   #EX: 9:29 --> 9, 9:30 --> 10
    hour, minute = str(time_str).split(":")

    new_minute = '00' + minute[2:]
    if int(minute[0]+minute[1]) < 30:
        new_time = f"{hour}:{new_minute}"
        return new_time

    else:
        new_hour = str(int(hour)+1)
        new_time = f"{new_hour}:{new_minute}"
        return new_time

i = 0
def dfprint(df, str):
    global i; i+=1
    print(f"\n({i}) ===== {str} =======\n{df.head(4)}")

def comment(str):
    global i; i+=1
    print(f"\n({i}) ===== {str} =======\n")

def main():
    df = pd.read_csv("behavior.csv")
    dfprint(df, "Original Data")

    df.columns = df.columns.str.replace(' ', '')
    dfprint(df, "Removed leading and Trailing Space (Error Handling)")

    df.drop(['deviceID', 'eventID'], axis=1, inplace=True)
    dfprint(df, "Removed USELESS columns (IDs doesn't help find behaviors)")

    df['time'] = df['time'].apply(lambda x: round_time(x))
    dfprint(df, "Rounded the time (repetitive behavior happens in similar time)")

    df.drop_duplicates(inplace=True)
    dfprint(df, "removed DUPLICATE rows (to avoid the anomaly of receiving same data twice)")

    oldDateType = df['date'].dtype
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    newDateType = df['date'].dtype
    dfprint(df, f"updated type of 'date' (to use datetime64 functions): {oldDateType} --> {newDateType}")
    comment("'time' functions are not needed. so it is kept as object")

main()