from datetime import datetime, timedelta

def get_nearest_workweek():
    ans = datetime.now()
    date =  ans.weekday()
    if date == 6:
        ans = ans - timedelta(days=2)
    elif date == 5:
        ans = ans - timedelta(days=1)
    return ans.strftime("%Y-%m-%d")


if __name__ == '__main__':
    print('hello')
    ans = get_nearest_workweek()
    print(ans)