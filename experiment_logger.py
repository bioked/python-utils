import csv
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class Experiment:
	def __init__(self, name):
		if not name:
			raise ValueError("Experiment must have a name")
		self.name = name
		self.participants = {}
		self.tasks = []

	def add_participant(self, pid, age):
		try:
			if not pid:
				raise ValueError("pid is required")
			if age <= 0:
				raise ValueError("age must be positive")
			if pid in self.participants:
				raise ValueError(f"duplicate participant id: {pid}")
			self.participants[pid] = {"age": age}
			logging.info(f"Added participant {pid} (age {age})")
		except ValueError as e:
			logging.error(f"add_participant failed: {e}")

	def log_task(self, pid, task, result):
		try:
			if pid not in self.participants:
				raise ValueError(f"unknown participant: {pid}")
			self.tasks.append({"id": pid, "task": task, "result": result})
			logging.info(f"Logged task '{task}' for {pid} -> {result}")
		except ValueError as e:
			logging.error(f"log_task failed: {e}")

	def save_results(self, path: Path):
		try:
			path.parent.mkdir(parents=True, exist_ok=True)
			with path.open("w", newline="", encoding="utf-8") as f:
				writer = csv.DictWriter(f, fieldnames=["id", "task", "result"])
				writer.writeheader()
				writer.writerows(self.tasks)
			logging.info(f"Saved {len(self.tasks)} tasks to {path}")
		except Exception as e:
			logging.error(f"save_results failed: {e}")

def main():
	exp = Experiment("Robotic Arm Control Study")

	# Operators (participants)
	exp.add_participant("Op01", 29)
	exp.add_participant("Op02", 33)

	# Arm control tasks
	exp.log_task("Op01", "Pick-and-place bolts", "success")
	exp.log_task("Op02", "Pick-and-place bolts", "fail")
	exp.log_task("Op01", "Precision soldering", "timeout")
	exp.log_task("Op02", "Assembly line tracking", "success")

	# Invalid operator to show error handling
	exp.log_task("Op99", "Welding test", "success")

	# Save results
	exp.save_results(Path("robot_arm_results.csv"))  

if __name__ == "__main__":
	main()
