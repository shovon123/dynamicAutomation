import pandas as pd
pd.set_option('display.max_rows', 10)

def round_time(time_str):                       #EX: 9:29 --> 9, 9:30 --> 10
    hour, minute = str(time_str).split(":")

    new_minute = '00' + minute[2:]              #minute[2:0] --> AM/PM
    if int(minute[0]+minute[1]) < 30:
        new_time = f"{hour}:{new_minute}"
        return new_time

    else:
        new_hour = str(int(hour)+1)
        new_time = f"{new_hour}:{new_minute}"
        return new_time

def dfprint(str):   print(f"\n======= {str} =======\n{df.head(4)}")

def comment(str):   print(f"\n======= {str} =======")

df = pd.read_csv("behavior.csv")

def main():
    dfprint(f"({0}) ORIGINAL Data")

    df.columns = df.columns.str.replace(' ', '')
    dfprint(f"({1}) Removed LEADING and TRAILING SPACE (Error Handling)")

    df.drop(['deviceID', 'eventID'], axis=1, inplace=True)
    dfprint(f"({2}) Removed USELESS COLUMNS (IDs doesn't help find behaviors)")

    df['time'] = df['time'].apply(lambda x: round_time(x))
    dfprint(f"({3}) ROUNDED the TIME (repetitive behavior happens in similar time)")

    df.drop_duplicates(inplace=True)
    dfprint(f"({4}) removed DUPLICATE ROWS (to avoid the anomaly of receiving same data twice)")

    oldDateType = df['date'].dtype
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    newDateType = df['date'].dtype
    dfprint(f"({5}) UPDATED TYPE of 'DATE' (to use datetime64 functions): {oldDateType} --> {newDateType}")
    comment(f"({6}) 'TIME' functions are NOT needed. so it is kept as object")

    df.sort_values(by=['date', 'time'], ascending=[True, True], inplace=True)
    dfprint(f"({7}) Sort by DATE and then by TIME (to observe behavior gradually)")

    df.insert(2, 'day', df['date'].dt.day_name())
    dfprint(f"({8}) ADDED DAY column (to find weekly pattern)")

    # add another column to hold WHAT THE REPETITIVE PATTER IS named "behavior"
    df['behavior'] = df['time'] + " " + df['day'] + " " + df['device'] + " " + df['action']
    dfprint(f"({9}) ADDED BEHAVIOR column (the column to be observed as repetitive)")

main()