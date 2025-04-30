import streamlit as st
import math
import re
import random
import openai

# 🔐 API setup
openai.api_key = st.secrets["OPENAI_API_KEY"]

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

# PAGE CONFIG
st.set_page_config(page_title="Reality Check 💘", layout="centered")
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
yearly_meet = st.slider("How many people are you willing to meet per year?", 0, 20, 5)

# -------------------- GPT PROMPTING FUNCTION --------------------
def get_gpt_percentile(prompt, model="gpt-4-turbo"):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You're a brutally honest, emotionally aware dating coach and data analyst. "
                        "Evaluate the dating appeal or rarity of the profile based on US standards. "
                        "Return ONLY a number between 0.1 and 100. No text. No symbols. No explanations."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )
        text = response.choices[0].message["content"].strip()
        match = re.search(r"(\d+(\.\d+)?)", text)
        if match:
            return float(match.group(1))
        return None
    except:
        return None

# -------------------- BUTTON + MAIN LOGIC --------------------
if st.button("💘 Calculate My Love Odds"):

    # PROMPTS for GPT
    user_prompt = f"""
    - Gender: {your_gender}
    - Height: {your_height_ft}'{your_height_inch}
    - Income: {your_income}
    - Education: {your_edu}
    - Fitness: {your_fitness} days/week
    - Job: (assume based on income)
    - Attractiveness: {your_attractiveness}/10
    - MBTI: {your_mbti}
    - State: {your_state}
    - Has kids: {your_kids}
    """

    ideal_prompt = f"""
    Estimate how rare this ideal partner is in the US dating pool.

    - Height at least: {ideal_height_ft}'{ideal_height_inch}
    - Income: above {ideal_income}
    - Fitness: {ideal_fitness} workouts/week
    - Education: {ideal_edu}
    - Animal lover: {ideal_animals}
    - Has kids: {ideal_kids}
    - MBTI: {ideal_mbti}
    - Physical attractiveness rating: {ideal_attractiveness}/10
    """

    # Get percentiles
    user_percentile = get_gpt_percentile(user_prompt)
    ideal_percentile = get_gpt_percentile(ideal_prompt)

    # --- Continue logic ---
    if user_percentile is None or ideal_percentile is None:
        st.error("Sorry, couldn't get a valid percentile from ChatGPT. Try again or check your API key.")
    else:
        # CONTINUE with main logic (use the corrected version you already have)
        st.success("🎯 GPT scoring worked! You can now continue with the result + roast + tip logic 💅")
