#!/usr/bin/env python3
import os
import random
import subprocess
from datetime import datetime, timedelta

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


def read_number():
    with open("number.txt", "r") as f:
        return int(f.read().strip())


def write_number(num):
    with open("number.txt", "w") as f:
        f.write(str(num))


def generate_random_commit_message():
    from transformers import pipeline

    generator = pipeline(
        "text-generation",
        model="gpt2-medium",  #        model="gpt2-medium",  # Better than gpt2, runs on CPU
        device="cpu",
    )
    prompt = """
        Generate a Git commit message following the Conventional Commits standard. The message should include a type, an optional scope, and a subject.Please keep it short. Here are some examples:

        - feat(auth): add user authentication module
        - fix(api): resolve null pointer exception in user endpoint
        - docs(readme): update installation instructions
        - chore(deps): upgrade lodash to version 4.17.21
        - refactor(utils): simplify date formatting logic

        Now, generate a new commit message: - """
    generated = generator(
        prompt,
        max_new_tokens=50,
        num_return_sequences=1,
        temperature=0.5,  # Slightly higher for creativity
        top_k=50,  # Limits sampling to top 50 logits
        top_p=0.9,  # Nucleus sampling for diversity
        truncation=True,
    )
    text = generated[0]["generated_text"]
    print(text)
    if "- " in text:
        return text.rsplit("- ", 1)[-1].strip()
    else:
        raise ValueError(f"Unexpected generated text {text}")


def git_commit():
    # Ensure git user.email is set
    subprocess.run(["git", "config", "--global", "user.email", "tom.marty@mila.quebec"])
    # Stage the changes
    subprocess.run(["git", "add", "number.txt"])
    # Create commit with current date
    if True:
        commit_message = generate_random_commit_message()
    else:
        date = datetime.now().strftime("%Y-%m-%d")
        commit_message = f"Update number: {date}"
    subprocess.run(["git", "commit", "-m", commit_message])


def git_push():
    # Push the committed changes to GitHub
    result = subprocess.run(["git", "push"], capture_output=True, text=True)
    if result.returncode == 0:
        print("Changes pushed to GitHub successfully.")
    else:
        print("Error pushing to GitHub:")
        print(result.stderr)


def get_next_weekday_time():
    """Generate random time, but if it falls on weekend, move to next Monday"""
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)

    # Start with tomorrow
    target_date = datetime.now().date() + timedelta(days=1)

    # If target date is Saturday (5) or Sunday (6), move to next Monday
    if target_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
        days_until_monday = 7 - target_date.weekday()
        target_date = target_date + timedelta(days=days_until_monday)

    return target_date, random_hour, random_minute


def update_cron_with_random_time():
    target_date, random_hour, random_minute = get_next_weekday_time()
    import sys

    if sys.platform.startswith("win"):
        # Windows Task Scheduler with WakeToRun
        import getpass
        import tempfile

        task_name = "UpdateNumberJob"
        script_path = os.path.join(script_dir, "update_number.py")
        python_path = sys.executable
        time_str = f"{random_hour:02d}:{random_minute:02d}"
        username = getpass.getuser()
        xml_content = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
    <RegistrationInfo>
        <Date>{datetime.now().isoformat()}</Date>
        <Author>{username}</Author>
    </RegistrationInfo>
    <Triggers>
        <TimeTrigger>
            <StartBoundary>{target_date}T{time_str}:00</StartBoundary>
            <Enabled>true</Enabled>
            <Repetition>
                <Interval>P1D</Interval>
                <StopAtDurationEnd>false</StopAtDurationEnd>
            </Repetition>
        </TimeTrigger>
    </Triggers>
    <Principals>
        <Principal id="Author">
            <UserId>{username}</UserId>
            <LogonType>InteractiveToken</LogonType>
            <RunLevel>LeastPrivilege</RunLevel>
        </Principal>
    </Principals>
    <Settings>
        <WakeToRun>true</WakeToRun>
        <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
        <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
        <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
        <AllowHardTerminate>true</AllowHardTerminate>
        <StartWhenAvailable>true</StartWhenAvailable>
        <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
        <IdleSettings>
            <StopOnIdleEnd>false</StopOnIdleEnd>
            <RestartOnIdle>false</RestartOnIdle>
        </IdleSettings>
        <Enabled>true</Enabled>
        <Hidden>false</Hidden>
        <AllowStartOnDemand>true</AllowStartOnDemand>
        <Priority>7</Priority>
    </Settings>
    <Actions Context="Author">
        <Exec>
            <Command>{python_path}</Command>
            <Arguments>{script_path}</Arguments>
        </Exec>
    </Actions>
</Task>
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml", mode="w", encoding="utf-16") as tmpxml:
            tmpxml.write(xml_content)
            xml_path = tmpxml.name
        cmd = f'schtasks /Create /F /TN {task_name} /XML "{xml_path}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        os.remove(xml_path)
        if result.returncode == 0:
            day_name = target_date.strftime("%A")
            print(
                f"Task Scheduler job set for {day_name} {target_date} at {time_str} with WakeToRun enabled."
            )
        else:
            print("Error setting Task Scheduler job:")
            print(result.stderr)
    else:
        # Unix cron logic
        import tempfile

        new_cron_command = f"{random_minute} {random_hour} {target_date.day} {target_date.month} * cd {script_dir} && python3 {os.path.join(script_dir, 'update_number.py')}\n"
        with tempfile.NamedTemporaryFile(delete=False, mode="w+") as tmpfile:
            cron_file = tmpfile.name
        os.system(f"crontab -l > {cron_file} 2>/dev/null || true")
        with open(cron_file, "r") as file:
            lines = file.readlines()
        with open(cron_file, "w") as file:
            for line in lines:
                if "update_number.py" not in line:
                    file.write(line)
            file.write(new_cron_command)
        os.system(f"crontab {cron_file}")
        os.remove(cron_file)
        day_name = target_date.strftime("%A")
        print(f"Cron job updated to run on {day_name} {target_date} at {random_hour}:{random_minute:02d}.")


def main():
    try:
        current_number = read_number()
        num_commits = random.randint(1, 3)
        print(f"Sampling {num_commits} commits for this run.")
        for i in range(num_commits):
            new_number = current_number + 1
            write_number(new_number)
            git_commit()
            current_number = new_number
        git_push()
        update_cron_with_random_time()
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
