# William Perez, STUDENT ID 001438917
import argparse
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
import logging
from logging import getLogger
from wgups.core.delivery_manager import DeliveryManager
from wgups.core.utils import ingest_packages_from_file, ingest_distances_from_file, ingest_locations_from_file

logger = getLogger(__name__)
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])

class WGUPSApp:
    def __init__(self, root, delivery_manager: DeliveryManager):
        self.root = root
        self.delivery_manager = delivery_manager
        self.root.title("WGUPS Algorithm GUI")

        # State variables
        self.running = False
        self.log_queue = []
        self.lock = threading.Lock()

        # Create GUI elements
        self.start_button = tk.Button(root, text="Run", command=self.start)
        self.start_button.pack(pady=5)

        self.step_button = tk.Button(root, text="Tick number of Seconds", command=self.step)
        self.step_button.pack(pady=5)

        self.package_status_button = tk.Button(root, text="Check Package Status", command=self.check_package_status)
        self.package_status_button.pack(pady=5)


        self.log_label = tk.Label(root, text="Log Messages:")
        self.log_label.pack(pady=5)

        self.log_window = scrolledtext.ScrolledText(root, height=40, width=150, state="disabled")
        self.log_window.pack(pady=5)

        # Periodically update the log window
        self.update_logs()

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.run_tick_loop, daemon=True).start()
            logger.info("Started the tick loop.")

    def pause(self):
        if self.running:
            self.running = False
            logger.info("Paused the tick loop.")
        self.update_logs()

    def step(self):
        self.pause()  # Ensure paused before stepping
        seconds = simpledialog.askinteger("Step", "Enter seconds to tick:")
        if seconds is not None:
            for _ in range(seconds):
                if self.delivery_manager.all_packages_delivered():
                    hours = self.delivery_manager.time // 3600
                    minutes = (self.delivery_manager.time % 3600) // 60
                    seconds = self.delivery_manager.time % 60
                    logger.info(f"Simulation complete. Time: {hours}:{minutes}:{seconds}")
                    logger.info(
                        f"All {len(self.delivery_manager.packages_delivered)} routes ran. ({len(self.delivery_manager.packages_delivered) - self.delivery_manager.total_packages} extra routes made for special deliveries)")

                    break
                self.delivery_manager.tick()
        self.update_logs()

    def check_package_status(self):
        # Prompt the user for a package ID
        package_id = simpledialog.askstring("Package ID", "Enter the Package ID:")
        if package_id:
            # Get the status of the package
            package = self.delivery_manager.get_status_for_package_id(package_id)
            # Show the result in a dialog box
            messagebox.showinfo("Package Status", f"Package ID: {package_id}\nStatus: {package}")



    def run_tick_loop(self):
        while self.running:
            if self.delivery_manager.all_packages_delivered():
                break
            self.delivery_manager.tick() # Adjust as needed

        # convert time to hh:mm:ss
        hours = self.delivery_manager.time // 3600
        minutes = (self.delivery_manager.time % 3600) // 60
        seconds = self.delivery_manager.time % 60
        logger.info(f"Simulation complete. Time: {hours}:{minutes}:{seconds}")
        logger.info(
            f"All {len(self.delivery_manager.packages_delivered)} routes ran. ({len(self.delivery_manager.packages_delivered) - self.delivery_manager.total_packages} extra routes made for special deliveries)")

    def update_logs(self):
        """
        Periodically update the log window with new messages.
        """
        with self.lock:
            while self.log_queue:
                message = self.log_queue.pop(0)
                self.log_window.configure(state="normal")
                self.log_window.insert(tk.END, message + "\n")
                self.log_window.configure(state="disabled")
                self.log_window.yview(tk.END)

        # Schedule the next log update
        self.root.after(100, self.update_logs)


def configure_logging(app):
    """
    Redirect logging output to the GUI's log window.
    """
    class QueueHandler(logging.Handler):
        def emit(self, record):
            msg = self.format(record)
            with app.lock:
                app.log_queue.append(msg)

        # Get the root logger

    root_logger = logging.getLogger()

    # Remove other handlers to avoid duplicate logs
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    # Add the QueueHandler
    queue_handler = QueueHandler()
    queue_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    root_logger.addHandler(queue_handler)

    # Set log level for the root logger
    root_logger.setLevel(logging.INFO)


def run_gui(delivery_manager: DeliveryManager):
    root = tk.Tk()
    app = WGUPSApp(root, delivery_manager)
    configure_logging(app)
    root.mainloop()

def run_cli(args, delivery_manager: DeliveryManager):
    delivery_manager.start()

def main()-> None:
    parser = argparse.ArgumentParser(description="WGUPS Delivery Manager")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run the application in CLI mode instead of GUI mode.",
    )
    args = parser.parse_args()

    # Create hash tables to store the package
    # In python, these are implemented as Dictionaries
    # These two helper functions create Lists of Dictionaries.
    package_data = ingest_packages_from_file()
    distance_data = ingest_distances_from_file()
    location_data = ingest_locations_from_file()
    delivery_manager = DeliveryManager(package_data, distance_data, location_data)

    if args.cli:
        run_cli(args, delivery_manager)
    else:
        run_gui(delivery_manager=delivery_manager)

    logger.info("All packages delivered")


if __name__ == '__main__':
    # check if CLI arguments are passed


    main()
