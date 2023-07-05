from app_core.statistic_logic import data_for_month, report_month

if __name__ == "__main__":
    tasks = data_for_month()
    for i in tasks:
        print(i)
        print('*'*20)
    report = report_month(tasks)
    for i, j in report.items():
        print(i, j)