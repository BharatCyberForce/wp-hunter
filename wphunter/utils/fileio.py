import os

class FileIO:
    @staticmethod
    def readinput(filepath): #Mass Target Inputs From Target File
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Target file not found: {filepath}")

        targets = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        targets.append(line)
            return targets
        except Exception as e:
            raise IOError(f"Error reading target file {filepath}: {e}")
