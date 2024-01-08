from datetime import datetime


def log(message: str):
    time_now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    logfile = open(f"./logs/log-{time_now}.txt", "w")
    print(f"[{datetime.now()}]", message)
    logfile.write(f"[{datetime.now()}] {message}\n")
    logfile.close()


# if __name__ == "__main__":
#     time_now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
#     logsfile = open(f"./logs/log-{time_now}.txt", "w")
#
#     logsfile.write(f"Start Simbiosis Simulation v0.4\n"
#                   f"Start Time: {time_now}\n\n\n"
#                   f"Runtime Logs:\n"
#                   f"{'-' * 60}\n")