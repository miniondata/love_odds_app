import streamlit as st
import math
import re
import random

# -------------------- GDP-based State Tiers --------------------
tier_1_states = {
    "California", "Texas", "New York", "Florida", "Illinois",
    "Pennsylvania", "Ohio", "Georgia", "Washington", "New Jersey",
    "Michigan", "North Carolina", "Virginia"
}

tier_2_states = {
    "Massachusetts", "Tennessee", "Arizona", "Indiana", "Missouri",
    "Wisconsin", "Colorado", "Minnesota", "South Carolina", "Alabama"
}

# 🧠 PAGE CONFIG
st.set_page_config(page_title="Love Odds Calculator 💘", layout="centered")
st.title("💘 What Are the Odds You'll Meet *The One*?")
st.caption("Let’s do the math on your dating standards vs reality. Brutally honest but loving. 💅")

# -------------------- Ideal Partner Input --------------------
st.subheader("✨ Your Ideal Partner")

st.markdown("**Partner's height is at least:**")
col1, col2 = st.columns(2)
with col1:
    ideal_height_ft = st.selectbox("Feet", list(range(4, 8)), index=2, key="ideal_ft")
with col2:
    ideal_height_inch = st.selectbox("Inches", list(range(0, 12)), index=6, key="ideal_in")

col1, col2 = st.columns([2, 1])
with col1:
    ideal_income = st.number_input("Partner's annual income (USD) is at least", min_value=10000, step=1000, value=60000, format="%d")
with col2:
    st.markdown(f"**${ideal_income:,}**")

ideal_fitness = st.slider("Workouts per week", 0, 7, 3)
ideal_edu = st.selectbox("Education level", ["High school", "Bachelor's", "Graduate"])
ideal_animals = st.radio("Animal lover?", ["Yes", "No", "Whatever"])
ideal_kids = st.radio("Do they have kids?", ["Yes", "No"])
ideal_attractiveness = st.slider("How attractive should they be? (1 = meh, 10 = model)", 1, 10, 7)
ideal_mbti = st.text_input("MBTI (e.g. ENFP)", max_chars=4)
st.markdown("[🧠 Not sure about MBTI? Explore types here](https://www.16personalities.com/personality-types)")

# -------------------- User Input --------------------
st.divider()
st.subheader("🪞You (Be honest, we won’t judge 😉)")

your_gender = st.selectbox("What is your gender?", ["Woman", "Man", "Non-binary / Other"])
your_attraction = st.selectbox("Who are you romantically interested in?", ["Men", "Women", "Everyone"])
your_age = st.number_input("Your age", min_value=18, max_value=100, step=1)

st.markdown("**Your height:**")
col3, col4 = st.columns(2)
with col3:
    your_height_ft = st.selectbox("Feet", list(range(4, 8)), index=2, key="you_ft")
with col4:
    your_height_inch = st.selectbox("Inches", list(range(0, 12)), index=6, key="you_in")

col1, col2 = st.columns([2, 1])
with col1:
    your_income = st.number_input("Your annual income (USD)", min_value=10000, step=1000, value=60000, format="%d")
with col2:
    st.markdown(f"**${your_income:,}**")

your_fitness = st.slider("Your workouts per week", 0, 7, 2)
your_edu = st.selectbox("Your education", ["High school", "Bachelor's", "Graduate"])
your_animals = st.radio("Do you love animals?", ["Yes", "No", "Whatever"])
your_kids = st.radio("Do you have kids?", ["Yes", "No"])

us_states = sorted(list(tier_1_states | tier_2_states | {
    "Alaska", "Arkansas", "Connecticut", "Delaware", "Hawaii", "Idaho", "Iowa", "Kansas",
    "Kentucky", "Louisiana", "Maine", "Mississippi", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Mexico", "North Dakota", "Oklahoma", "Oregon", "Rhode Island",
    "South Dakota", "Utah", "Vermont", "West Virginia", "Wyoming"
}))
your_state = st.selectbox("Your state (US only)", us_states)

your_attractiveness = st.slider("How attractive are you? (1 = troll, 10 = hot hot hot)", 1, 10, 6)
your_mbti = st.text_input("Your MBTI", max_chars=4)
st.markdown("[💡 Explore MBTI types](https://www.16personalities.com/personality-types)")

monthly_meet = st.slider("How many people are you willing to meet per month?", 0, 50, 5)

# -------------------- Scoring Logic --------------------
def estimate_user_percentile():
    score = 0

    if your_edu == "Graduate": score += 2
    elif your_edu == "Bachelor's": score += 1

    try:
        if your_income >= 150000: score += 3
        elif your_income >= 100000: score += 2
        elif your_income >= 60000: score += 1
    except:
        pass

    if your_fitness >= 5: score += 2
    elif your_fitness >= 2: score += 1

    height_in_inches = (your_height_ft * 12) + your_height_inch
    if your_gender == "Man":
        if height_in_inches >= 75: score += 2
        elif height_in_inches >= 70: score += 1
    else:
        if height_in_inches >= 66: score += 1

    if your_attractiveness >= 9: score += 2
    elif your_attractiveness >= 7: score += 1

    mbti = your_mbti.upper()
    if len(mbti) == 4:
        if your_gender == "Man":
            if mbti[0] == "E": score += 1
            if mbti[2] == "T": score += 1
        elif your_gender == "Woman":
            if mbti[0] == "E": score += 1
            if mbti[2] == "F": score += 1

    if your_kids == "No": score += 1
    if your_animals == "No": score -= 1

    if your_state in tier_1_states:
        score += 2
    elif your_state in tier_2_states:
        score += 1

    noise = random.uniform(-1.5, 1.5)
    percentile = 100 - (score / 15 * 100) + noise
    return round(min(max(percentile, 0.1), 99.9), 1), score

# -------------------- Final Result --------------------
if st.button("💘 Calculate My Love Odds"):
    user_percentile, raw_score = estimate_user_percentile()

    ideal_score = ideal_fitness + ideal_attractiveness + (2 if ideal_edu == "Graduate" else 1 if ideal_edu == "Bachelor's" else 0)
    ideal_percentile = max(0.001, min(1, 1 - ideal_score / 20))

    n = monthly_meet * 12
    P = 1 - (1 - ideal_percentile) ** n
    P_percent = round(P * 100, 2)

    st.success("🎯 Results Are In! Let’s see how delulu you are...")
    st.markdown(f"**You're in the top `{user_percentile}%` of daters.**")
    true_rank = round(100 - user_percentile, 1)

    # Compatibility factor: the better you are, the higher your chances actually are
    compatibility_factor = true_rank / 100
    P_adjusted = round(P_percent * compatibility_factor, 2)
    
    if true_rank >= 90:
        roast = "🦄 A literal unicorn. They’re not ready for you."
    elif true_rank >= 70:
        roast = "🌟 Main character energy with ick management issues."
    elif true_rank >= 50:
        roast = "🎭 Mid-tier hottie with room for growth."
    elif true_rank >= 30:
        roast = "📉 You’re dating-app purgatory. Swipeable but forgettable."
    elif true_rank >= 10:
        roast = "🙃 You’re someone’s type, but it’s probably not your type."
    else:
        roast = "😬 You’re... brave. Good luck out there."

    st.markdown(f"**{roast}**")
    st.markdown(f"**Your ideal partner is in the top `{round(ideal_percentile * 100, 2)}%` rarity.**")
    st.markdown(f"**Your chance of meeting them in a year: `{P_adjusted}%`** 🎯")

    if P_adjusted > 0:
        expected_people = int(1 / (ideal_percentile * compatibility_factor))
        st.markdown(f"👻 That means if you ghost roughly `{expected_people}`** people this year — one of them might actually be Prince/ss Charming, not just another situationship 💁‍♀️")
    
    if P_adjusted < 50:
        if monthly_meet < 50:
            new_meet = min(monthly_meet + 10, 50)
            new_n = new_meet * 12
            new_odds = 1 - (1 - ideal_percentile) ** new_n
            new_adjusted = round((new_odds * 100) * compatibility_factor, 2)
            st.markdown(f"🧠 Tip: Increase your monthly interactions from {monthly_meet} to {new_meet} and your odds could improve to `{new_adjusted:.2f}%`.")
        else:
            st.markdown("🧠 Tip: You’re already meeting enough people — maybe your standards are bottlenecking the fantasy 💀")
    elif P_adjusted < 90:
        weakest = "something you’re not listing"
        st.markdown(f"📈 Tip: You’re close! Improving just one trait — maybe {weakest} — could push you over the edge.")
    else:
        if true_rank >= 90:
            st.markdown("💅 Tip: You’re perfect, baby. Manifest harder or raise your standards — you've earned it ✨")
        else:
            st.markdown("🫣 Tip: The math says yes. The vibes say... swipe wisely.")

    st.markdown("---")
    if P_percent > 50:
        st.success("💘 Conclusion: You're either a hot commodity or just realistic. Keep going, Cupid!")
    elif P_percent > 20:
        st.info("🧐 Conclusion: You're choosy, but not delulu.")
    else:
        st.warning("😵‍💫 Conclusion: Babe... your standards are giving ✨fictional character✨.")
