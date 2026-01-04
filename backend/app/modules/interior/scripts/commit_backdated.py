import subprocess
import os
import math

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        with open("error_log.txt", "w") as f:
            f.write(f"Error executing command: {command}\n")
            f.write(f"STDOUT: {e.stdout}\n")
            f.write(f"STDERR: {e.stderr}\n")
        print("Error logged to error_log.txt")
        return None

def main():
    # Get status
    status_output = run_command("git status --porcelain")
    if not status_output:
        print("No changes to commit.")
        return

    files = []
    for line in status_output.split('\n'):
        if line.strip():
            # Status is first 2 chars, then space, then path
            # Handle cases with spaces in path (though unlikely for our assets)
            # Porcelain format: XY PATH
            # XY is always 2 chars. Then space.
            # But sometimes it might be tricky.
            # Safer: take from index 2 and strip whitespace.
            path = line[2:].strip()
            # Remove quotes if present (for paths with spaces)
            path = path.strip('"')
            files.append(path)

    print(f"Found {len(files)} files to commit.")

    # Split into two batches
    mid_point = math.ceil(len(files) / 2)
    batch1 = files[:mid_point]
    batch2 = files[mid_point:]

    date1 = "2025-12-30 12:00:00"
    date2 = "2026-01-01 12:00:00"

    print(f"Batch 1 ({len(batch1)} files) -> {date1}")
    print(f"Batch 2 ({len(batch2)} files) -> {date2}")

    # Commit Batch 1
    for file_path in batch1:
        print(f"Committing {file_path} on {date1}...")
        run_command(f'git add "{file_path}"')
        # Use filename as message
        filename = os.path.basename(file_path)
        msg = f"Add {filename}"
        # Set GIT_COMMITTER_DATE and --date for author date
        env_cmd = f'set GIT_COMMITTER_DATE="{date1}" && git commit -m "{msg}" --date="{date1}"'
        # Note: 'set' is for Windows cmd. For PowerShell we might need different syntax, 
        # but run_command uses shell=True which often defaults to cmd on Windows unless specified.
        # Let's try to be shell agnostic or assume standard windows shell.
        # Actually, passing env vars in subprocess is better.
        
        # We will use subprocess with env argument
        env = os.environ.copy()
        env["GIT_COMMITTER_DATE"] = date1
        subprocess.run(f'git commit -m "{msg}" --date="{date1}"', shell=True, env=env, check=True)

    # Commit Batch 2
    for file_path in batch2:
        print(f"Committing {file_path} on {date2}...")
        run_command(f'git add "{file_path}"')
        filename = os.path.basename(file_path)
        msg = f"Add {filename}"
        
        env = os.environ.copy()
        env["GIT_COMMITTER_DATE"] = date2
        subprocess.run(f'git commit -m "{msg}" --date="{date2}"', shell=True, env=env, check=True)

    print("All commits completed.")

if __name__ == "__main__":
    main()
