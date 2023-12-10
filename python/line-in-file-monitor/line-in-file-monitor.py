import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher(FileSystemEventHandler):
    def __init__(self, filename, pattern):
        self.filename = filename
        self.pattern = pattern
        self.previous_line = ""

    def on_modified(self, event):
        if event.src_path == self.filename:
            with open(self.filename, 'r') as f:
                for line in f:
                    if self.pattern in line and line != self.previous_line:
                        print("Line has changed")
                        self.previous_line = line

if __name__ == "__main__":
    path = "/home/fredrik/test.txt"
    pattern = "test"

    event_handler = Watcher(path, pattern)
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()