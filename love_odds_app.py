import streamlit as st
import math
import re
import random
import openai

# 🔐 Replace with your actual OpenAI API Key if needed
openai.api_key = st.secrets["OPENAI_API_KEY"]

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
your_state = st.text_input("Your state (US only)", placeholder="e.g. California")
your_attractiveness = st.slider("How attractive are you? (1 = troll, 10 = hot hot hot)", 1, 10, 6)
your_mbti = st.text_input("Your MBTI", max_chars=4)
st.markdown("[💡 Explore MBTI types](https://www.16personalities.com/personality-types)")

monthly_meet = st.slider("How many people are you willing to meet per month?", 0, 100, 5)

# -------------------- Ranking System --------------------
def estimate_user_percentile():
    score = 0
    if your_edu == "Graduate": score += 2
    elif your_edu == "Bachelor's": score += 1

    try:
        income_val = int(re.sub(r"\D", "", your_income))
        if income_val >= 150000: score += 3
        elif income_val >= 100000: score += 2
        elif income_val >= 60000: score += 1
    except:
        pass

    if your_fitness >= 5: score += 2
    elif your_fitness >= 2: score += 1

    try:
        height_ft = float(your_height.replace("'", ".").replace("ft", "").strip())
        if your_gender == "Man":
            if height_ft >= 6.0: score += 2
            elif height_ft >= 5.8: score += 1
        else:
            if height_ft >= 5.6: score += 1
    except:
        pass

    high_gdp_states = {"California", "Texas", "New York", "Florida", "Illinois"}
    if your_state.strip() in high_gdp_states: score += 1

    mbti = your_mbti.upper()
    if len(mbti) == 4:
        if your_gender == "Man":
            if mbti[0] == "E": score += 1
            if mbti[2] == "T": score += 1
        elif your_gender == "Woman":
            if mbti[0] == "E": score += 1
            if mbti[2] == "F": score += 1

    score += your_attractiveness - 5
    score = max(0, min(score, 15))
    noise = random.uniform(-1.5, 1.5)
    percentile = (score / 15 * 100) + noise
    return round(min(max(percentile, 0.1), 99.9), 1), score

# -------------------- GPT Vibe Check --------------------
def get_gpt_vibe_score_and_feedback(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You're an honest but emotionally intelligent dating coach. Return a percentile (0.1–100) and one short line of feedback, separated by a dash."},
                {"role": "user", "content": prompt}
            ]
        )
        text = response.choices[0].message.content.strip()
        match = re.search(r"(\d+(\.\d+)?)\s*[-–—]\s*(.*)", text)
        if match:
            score = float(match.group(1))
            comment = match.group(3).strip()
            return score, comment
    except:
        return 50.0, "You're doing okay, babe. Could be worse."

# -------------------- Result --------------------
if st.button("💘 Calculate My Love Odds"):
    user_percentile, raw_score = estimate_user_percentile()

    vibe_prompt = f"""
    Evaluate the dating market value of the following person in the US context. Be encouraging if top-tier, but realistic if average or below. Return a percentile and a short comment.

    Gender: {your_gender}
    Age: {your_age}
    Height: {your_height}
    Income: {your_income}
    Fitness: {your_fitness} workouts/week
    Education: {your_edu}
    Job: {your_job}
    State: {your_state}
    MBTI: {your_mbti}
    Attractiveness: {your_attractiveness}/10
    Kids: {your_kids}
    """

    vibe_percentile, vibe_comment = get_gpt_vibe_score_and_feedback(vibe_prompt)

    final_percentile = round(min(max((user_percentile * 0.85 + vibe_percentile * 0.15 + random.uniform(-1.5, 1.5)), 0.1), 99.9), 1)

    ideal_score = ideal_fitness + ideal_attractiveness + (2 if ideal_edu == "Graduate" else 1 if ideal_edu == "Bachelor's" else 0)
    ideal_percentile = max(0.001, min(1, 1 - ideal_score / 20))

    n = monthly_meet * 12
    P = 1 - (1 - ideal_percentile) ** n
    P_percent = round(P * 100, 2)

    st.success("🎯 Results Are In! Let’s see how delulu you are...")
    st.markdown(f"**You're in the top {final_percentile}% of daters.**")
    st.markdown(f"*GPT’s vibe check:* `{vibe_percentile}%` – _{vibe_comment}_")

    if final_percentile <= 10:
        roast = "😬 You’re... brave. Good luck out there."
    elif final_percentile <= 30:
        roast = "🙃 You’re someone’s type, but it’s probably not your type."
    elif final_percentile <= 50:
        roast = "📉 You’re dating-app purgatory. Swipeable but forgettable."
    elif final_percentile <= 70:
        roast = "🎭 Mid-tier hottie with room for growth."
    elif final_percentile <= 90:
        roast = "🌟 Main character energy with ick management issues."
    else:
        roast = "🦄 A literal unicorn. They’re not ready for you."

    st.markdown(f"**{roast}**")
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

    st.markdown("---")
    if P_percent > 50:
        st.success("💘 Conclusion: You're either a hot commodity or just realistic. Keep going, Cupid!")
    elif P_percent > 20:
        st.info("🧐 Conclusion: You're choosy, but not delulu.")
    else:
        st.warning("😵‍💫 Conclusion: Babe... your standards are giving ✨fictional character✨.")
