from datetime import datetime

time_now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
logfile = open(f"./logs/log-{time_now}.txt", "w")

logfile.write(f"Start Simbiosis Simulation v1.0\n"
              f"Start Time: {time_now}\n\n\n"
              f"Runtime Logs:\n"
              f"{'-' * 60}\n")


def log(message: str):
    print(f"[{datetime.now()}]", message)
    logfile.write(f"[{datetime.now()}] {message}\n")

# if __name__ == "__main__":
#     time_now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
#     logsfile = open(f"./logs/log-{time_now}.txt", "w")
#
#     logsfile.write(f"Start Simbiosis Simulation v0.4\n"
#                   f"Start Time: {time_now}\n\n\n"
#                   f"Runtime Logs:\n"
#                   f"{'-' * 60}\n")
