import streamlit as st
from openai import OpenAI
import math
import re

# 🔐 API connection
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 🧠 PAGE CONFIG
st.set_page_config(page_title="Love Odds Calculator 💘", layout="centered")
st.title("💘 What Are the Odds You'll Meet *The One*?")
st.caption("Let’s do the math on your dating standards vs reality. Brutally honest but loving. 💅")

# -------------------- Ideal Partner Input --------------------
st.subheader("✨ Your Ideal Partner")

ideal_height = st.text_input("Height range", placeholder="e.g. 5'10 to 6'3")
ideal_income = st.text_input("Income range", placeholder="e.g. $100k to $250k")
ideal_fitness = st.slider("Workouts per week", 0, 7, 3)
ideal_edu = st.selectbox("Education level", ["High school", "Bachelor's", "Graduate"])
ideal_animals = st.radio("Animal lover?", ["Yes", "No", "Whatever"])
ideal_kids = st.radio("Do they have kids?", ["Yes", "No", "No and don't want kids"])
ideal_locations = st.text_input("Preferred locations (US only)", placeholder="e.g. New York, California")
ideal_attractiveness = st.slider("How attractive should they be? (1 = meh, 10 = model)", 1, 10, 7)
ideal_mbti = st.text_input("MBTI (e.g. ENFP)", max_chars=4)
st.markdown("[🧠 Not sure about MBTI? Explore types here](https://www.16personalities.com/personality-types)")
st.markdown("MBTI is made up of 4 elements. For each one, choose one of the two: **(I/E)** Introvert or Extrovert, **(S/N)** Sensing or Intuition, **(T/F)** Thinking or Feeling, **(P/J)** Perceiving or Judging.")

# -------------------- User Input --------------------
st.divider()
st.subheader("🪞You (Be honest, we won’t judge 😉)")

your_gender = st.selectbox("What is your gender?", ["Woman", "Man", "Non-binary / Other"])
your_attraction = st.selectbox("Who are you romantically interested in?", ["Men", "Women", "Everyone"])
your_age = st.number_input("Your age", min_value=18, max_value=100, step=1)
your_job = st.text_input("Your job or profession")
your_height = st.text_input("Your height", placeholder="e.g. 5'4 or 6.1")
your_income = st.text_input("Your income range", placeholder="e.g. $60k to $90k")
your_fitness = st.slider("Your workouts per week", 0, 7, 2)
your_edu = st.selectbox("Your education", ["High school", "Bachelor's", "Graduate"])
your_animals = st.radio("Do you love animals?", ["Yes", "No", "Whatever"])
your_kids = st.radio("Do you have kids?", ["Yes", "No", "No and don't want kids"])
your_city = st.text_input("Your city (must be within the US)", placeholder="e.g. Austin")
your_mbti = st.text_input("Your MBTI", max_chars=4)
st.markdown("[💡 Explore MBTI types](https://www.16personalities.com/personality-types)")
st.markdown("MBTI is made up of 4 elements. For each one, choose one of the two: **(I/E)** Introvert or Extrovert, **(S/N)** Sensing or Intuition, **(T/F)** Thinking or Feeling, **(P/J)** Perceiving or Judging.")

monthly_meet = st.slider("How many people are you willing to meet per month?", 0, 100, 5)

# -------------------- Submit + Result --------------------
if st.button("💘 Calculate My Love Odds"):

    with st.spinner("Consulting the stars, stats, and spreadsheets..."):

        def get_percentile(prompt):
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a brutally honest, data-driven dating analyst. You are not here to be nice. Rank users strictly based on US dating market value, factoring height, income, fitness, and education. Do NOT overvalue emotional or rare personality traits. Respond only based on real-world attractiveness and desirability statistics in the US."
                    },
                    {"role": "user", "content": prompt}
                ]
            )
            text = response.choices[0].message.content.strip()
            match = re.search(r"(\d+(\.\d+)?)", text)
            if match:
                return float(match.group(1))
            else:
                raise ValueError(f"Could not extract number from response: {text}")

        # --- Prompt: Ideal Partner ---
        ideal_prompt = f"""
        Estimate how rare this ideal partner is in the US dating pool.

        Respond with ONLY a number between 0.1 and 100 — no explanation, no symbols, just the number.

        Traits:
        - Height: {ideal_height}
        - Income: {ideal_income}
        - Fitness: {ideal_fitness} workouts/week
        - Education: {ideal_edu}
        - Animal lover: {ideal_animals}
        - Has kids: {ideal_kids}
        - Locations: {ideal_locations}
        - MBTI: {ideal_mbti}
        - Physical attractiveness rating: {ideal_attractiveness}/10
        """

        # --- Prompt: User ---
        user_prompt = f"""
        Estimate this person's dating percentile in the US only. Be BRUTAL and strictly logical — do not flatter.

        Respond with ONLY a number between 0.1 and 100 — no explanation, no symbols, just the number.

        Traits:
        - Gender/Preference: {your_gender}, attracted to {your_attraction}
        - Age: {your_age}
        - Job: {your_job}
        - Height: {your_height}
        - Income: {your_income}
        - Fitness: {your_fitness} workouts/week
        - Education: {your_edu}
        - Animal lover: {your_animals}
        - Has kids: {your_kids}
        - City: {your_city} (within the US)
        - MBTI: {your_mbti}
        """

        try:
            ideal_percentile = get_percentile(ideal_prompt) / 100
            user_percentile = get_percentile(user_prompt)

            n = monthly_meet * 12
            P = 1 - (1 - ideal_percentile) ** n
            P_percent = round(P * 100, 2)

            # 🎯 Results
            st.success("🎯 Results Are In! Let’s see how delulu you are...")

            st.markdown(f"**You're in the top {round(user_percentile, 1)}% of daters.**")
            st.markdown(f"**Your ideal partner is in the top {round(ideal_percentile * 100, 2)}% rarity.**")
            st.markdown(f"**Your chance of meeting them in a year: `{P_percent}%`** 🎯")

            if P_percent > 0:
                expected_people = int(1 / ideal_percentile)
                st.markdown(f"💡 That means if you ghost roughly **{expected_people}** people this year — one of them might actually be Prince/ss Charming, not just another situationship 💁‍♀️")

            if monthly_meet < 30:
                new_meet = monthly_meet + 10
                new_n = new_meet * 12
                new_odds = 1 - (1 - ideal_percentile) ** new_n
                st.markdown(f"🧠 Tip: If you increased your monthly interactions from {monthly_meet} to {new_meet}, your odds could improve to about `{round(new_odds * 100, 2)}%`. Just saying.")

            if ideal_percentile < 0.005:
                st.markdown("📉 Your standards are elite. Consider widening your ideal criteria just a tiny bit to increase your odds!")

            # 🥲 Final Funny Summary
            st.markdown("---")
            if P_percent > 50:
                st.success("💘 Conclusion: You're either a hot commodity or just realistic. Keep going, Cupid!")
            elif P_percent > 20:
                st.info("🧐 Conclusion: Not bad. You’re choosy, but not delulu.")
            else:
                st.warning("😵‍💫 Conclusion: Babe... your standards are giving ✨fictional character✨.")

        except Exception as e:
            st.error(f"Something went wrong: {e}")
