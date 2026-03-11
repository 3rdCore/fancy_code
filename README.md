

So, you’ve found my secret project. Congratulations. 🕵️‍♂️

This little script does exactly what you think it does: it increments a number in a file every single day, commits the change to Git, and then *magically* schedules itself to run again at some random time tomorrow.

Yes, that means you get a glorious **green square** every day on GitHub ✅.
And yes, dear future employer who is definitely reading this right now 👀… this repo is basically just a glorified **commit streak machine**.

👉 Please, *please* also check my other projects if you want to see actual work that required thinking. This one’s just here to feed the algorithmic gods of GitHub. 🙏

---

## Setup 🛠️
This code was adapted to run on Windows using Task Scheduler. If you’re on Linux or Mac, you can use `cron` instead.

1. Clone this repo (don’t ask why):

   ```bash
   git clone https://github.com/Shogun89/fancy_job
   cd fancy_job
   ```

2. Run the script:

   ```bash
   python update_number.py
   ```

   (Yes, it’s that dumb. No, it doesn’t need fancy dependencies… unless you want them, in which case read on.)

3. **Optional, but absurdly over-engineered:**
   If you want AI-generated commit messages because *why not*, install [uv](https://docs.astral.sh/uv) and do:

   ```bash
   set FANCY_JOB_USE_LLM=true uv run python update_number.py
   ```

   Boom. Now your profile will look “active” while you’re still asleep. 🛌💤

---

## Usage 🎉

* Increments the number in `number.txt` 📄
* Commits to Git with or without the help of a robot 🤖
* Repeats forever, or at least until you actually get a job 💼

⚠️ **Disclaimer to recruiters / employers:**
This project is satire. If you’re impressed by this repo, we need to talk. Please look at literally anything else I’ve built.


