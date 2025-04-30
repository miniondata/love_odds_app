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

ideal_height = st.number_input("Partner height above (in feet)", min_value=5.0, max_value=7.5, value=5.8, step=0.1)
ideal_income = st.slider("Ideal Partner Income", min_value=20000, max_value=1000000, step=10000, value=100000)
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
your_height_feet = st.number_input("Your height (feet)", min_value=4, max_value=7, step=1, value=5)
your_height_inches = st.number_input("Your height (inches)", min_value=0, max_value=11, step=1, value=6)
your_income = st.number_input("Your income (USD per year)", min_value=10000, step=1000, value=60000)
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
    traits = {}

    # TIER System for Education
    if your_edu == "Graduate":
        score += 2
        traits["education"] = "Graduate"
    elif your_edu == "Bachelor's":
        score += 1
        traits["education"] = "Bachelor's"
    else:
        traits["education"] = "High School"

    # TIER System for Income
    if your_income >= 150000:
        score += 3
        traits["income"] = "Elite"
    elif your_income >= 100000:
        score += 2
        traits["income"] = "High"
    elif your_income >= 60000:
        score += 1
        traits["income"] = "Average"
    else:
        traits["income"] = "Low"

    # TIER System for Fitness
    if your_fitness >= 6:
        score += 2
        traits["fitness"] = "Elite"
    elif your_fitness >= 4:
        score += 1
        traits["fitness"] = "High"
    elif your_fitness >= 2:
        traits["fitness"] = "Average"
    else:
        traits["fitness"] = "Low"

    # TIER System for Height
    height_in_inches = (your_height_feet * 12) + your_height_inches
    if your_gender == "Man":
        if height_in_inches >= 75:  # 6'3"
            score += 2
            traits["height"] = "Elite"
        elif height_in_inches >= 70:  # 5'10"
            score += 1
            traits["height"] = "High"
        else:
            traits["height"] = "Average"
    else:
        if height_in_inches >= 66:  # 5'6"
            score += 1
            traits["height"] = "High"
        else:
            traits["height"] = "Average"

    # TIER System for Location
    high_gdp_states = {"California", "Texas", "New York", "Florida", "Illinois"}
    if your_state.strip() in high_gdp_states:
        score += 1
        traits["location"] = "High GDP"

    # TIER System for Attractiveness
    if your_attractiveness >= 9:
        score += 2
        traits["attractiveness"] = "Elite"
    elif your_attractiveness >= 7:
        score += 1
        traits["attractiveness"] = "High"
    elif your_attractiveness >= 5:
        traits["attractiveness"] = "Average"
    else:
        traits["attractiveness"] = "Low"

    # TIER System for MBTI (E > I for men, T > F for women)
    mbti = your_mbti.upper()
    if len(mbti) == 4:
        if your_gender == "Man":
            if mbti[0] == "E": 
                score += 1
                traits["mbti"] = "E"
            if mbti[2] == "T": 
                score += 1
                traits["mbti"] = "T"
        elif your_gender == "Woman":
            if mbti[0] == "E": 
                score += 1
                traits["mbti"] = "E"
            if mbti[2] == "F": 
                score += 1
                traits["mbti"] = "F"

    # Adjust Score with Noise
    score = max(0, min(score, 15))
    noise = random.uniform(-1.5, 1.5)
    percentile = 100 - (score / 15 * 100) + noise
    return round(min(max(percentile, 0.1), 99.9), 1), score, traits

# -------------------- Result --------------------
if st.button("💘 Calculate My Love Odds"):
    user_percentile, raw_score, traits = estimate_user_percentile()

    final_percentile = round(min(max(user_percentile, 0.1), 99.9), 1)

    ideal_score = ideal_fitness + ideal_attractiveness + (2 if ideal_edu == "Graduate" else 1 if ideal_edu == "Bachelor's" else 0)
    ideal_percentile = max(0.001, min(1, 1 - ideal_score / 20))

    n = monthly_meet * 12
    P = 1 - (1 - ideal_percentile) ** n
    P_percent = round(P * 100, 2)

    st.success("🎯 Results Are In! Let’s see how delulu you are...")
    st.markdown(f"**You're in the top {final_percentile}% of daters.**")

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
