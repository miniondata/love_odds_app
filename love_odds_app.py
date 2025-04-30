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
your_attractiveness = st.slider("How attractive are you? (1 = troll, 10 = hot hot hot)", 1, 10, 6)
your_mbti = st.text_input("Your MBTI", max_chars=4)
st.markdown("[💡 Explore MBTI types](https://www.16personalities.com/personality-types)")

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
                        "content": "You're a brutally honest, emotionally aware dating coach and data analyst. "
                                    "You evaluate dating profiles using realistic US dating standards: income, height, education, attractiveness, fitness, job prestige, and personality. "
                                    "You never flatter. You do not overvalue rare traits or soft factors. "
                                    "Weight the following:\n"
                                    "- For **men**: height and income matter the most.\n"
                                    "- For **women**: physical attractiveness and charm matter more.\n"
                                    "- High GDP states (like CA, NY, TX, FL, IL) give a small boost.\n"
                                    "- MBTI: extrovert > introvert, T > F for men, F > T for women.\n"
                                    "You must return ONLY a percentile number between 0.1 and 100. No explanation. No symbols. Just the number."
                    },
                    {"role": "user", "content":(
                                f"- Gender: {gender}\n"
                                f"- Height: {height}\n"
                                f"- Income: {income}\n"
                                f"- Education: {education}\n"
                                f"- Fitness: {fitness} days/week\n"
                                f"- Job: {job}\n"
                                f"- Attractiveness (self-rated): {attractiveness}/10\n"
                                f"- MBTI: {mbti}\n"
                                f"- State: {state}\n"
                                f"- Has kids: {kids}"
                    )
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
        - Job: {your_job} (assess for prestige and income security)
        - Height: {your_height}
        - Income: {your_income}
        - Fitness: {your_fitness} workouts/week
        - Education: {your_edu}
        - City: {your_city} (assess dating pool size)
        - Physical attractiveness rating (self-reported): {your_attractiveness}/10
        - Animal lover: {your_animals}
        - Has kids: {your_kids}
        - MBTI: {your_mbti}
        """

        try:
            ideal_percentile = get_percentile(ideal_prompt) / 100
            user_prompt = f"""
            Evaluate this person's dating percentile in the US only. Use logic, not vibes.

            Criteria weighting:
            - For men: height and income matter most
            - For women: physical attractiveness and social fit matter more
            - Extroverts > introverts; T > F for men, F > T for women
            - High-GDP states (e.g. CA, NY, TX, FL) = mild bonus
            - Fitness, job prestige, and education also count
            - DO NOT FLATTER OR ROUND UP. Return a harsh but realistic percentile.

            Return ONLY a number between 0.1 and 100. No explanation, no symbols.

            Profile:
            - Gender: {your_gender}
            - Height: {your_height}
            - Income: {your_income}
            - Education: {your_edu}
            - Fitness: {your_fitness} workouts/week
            - Job: {your_job}
            - Attractiveness (self-rated): {your_attractiveness}/10
            - MBTI: {your_mbti}
            - State: {your_city}
            - Has kids: {your_kids}
            """
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
