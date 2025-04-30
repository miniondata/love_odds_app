import streamlit as st
import openai
import math
import re

# -------------------- API Setup --------------------
openai.api_key = st.secrets["OPENAI_API_KEY"]

# -------------------- Page Setup --------------------
st.set_page_config(page_title="Reality Check 💘", layout="centered")
st.title("💘 What Are the Odds You'll Meet *The One*?")
st.caption("Let’s do the math on your dating standards vs reality. Brutally honest but loving. 💅")

# -------------------- Ideal Partner Section --------------------
st.subheader("✨ Your Ideal Partner")
st.markdown("**Partner's height is at least:**")
col1, col2 = st.columns(2)
with col1:
    ideal_height_ft = st.selectbox("Feet", list(range(4, 8)), index=2)
with col2:
    ideal_height_in = st.selectbox("Inches", list(range(0, 12)), index=6)
ideal_income = st.number_input("Partner's minimum income (USD/year)", min_value=10000, value=60000, step=1000, format="%d")
ideal_fitness = st.slider("Partner's workouts per week", 0, 7, 3)
ideal_edu = st.selectbox("Partner's education level", ["High school", "Bachelor's", "Graduate"])
ideal_animals = st.radio("Partner loves animals?", ["Yes", "No", "Whatever"])
ideal_kids = st.radio("Partner has kids?", ["Yes", "No"])
ideal_attractiveness = st.slider("Partner's attractiveness (1 = meh, 10 = model)", 1, 10, 7)
ideal_mbti = st.text_input("Partner MBTI (optional)", max_chars=4)

# -------------------- You Section --------------------
st.divider()
st.subheader("🪞 You (Be honest, we won’t judge 😉)")
your_gender = st.selectbox("Your gender", ["Woman", "Man", "Non-binary / Other"])
your_attraction = st.selectbox("Who are you interested in?", ["Men", "Women", "Everyone"])
your_age = st.number_input("Your age", min_value=18, max_value=100, step=1)

st.markdown("**Your height:**")
col3, col4 = st.columns(2)
with col3:
    your_height_ft = st.selectbox("Feet", list(range(4, 8)), index=2, key="your_ft")
with col4:
    your_height_in = st.selectbox("Inches", list(range(0, 12)), index=6, key="your_in")

your_income = st.number_input("Your income (USD/year)", min_value=10000, value=60000, step=1000, format="%d")
your_fitness = st.slider("Your workouts per week", 0, 7, 2)
your_edu = st.selectbox("Your education", ["High school", "Bachelor's", "Graduate"])
your_animals = st.radio("Do you love animals?", ["Yes", "No", "Whatever"])
your_kids = st.radio("Do you have kids?", ["Yes", "No"])
your_state = st.text_input("Your US State", placeholder="e.g. California")
your_attractiveness = st.slider("Your attractiveness (1 = troll, 10 = hot hot hot)", 1, 10, 6)
your_mbti = st.text_input("Your MBTI (optional)", max_chars=4)
yearly_meet = st.slider("How many people are you willing to meet per year?", 0, 20, 5)

# -------------------- ChatGPT Scoring --------------------
def get_percentile(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You're a brutally honest, emotionally aware dating coach and data analyst. "
                           "You return ONLY a percentile between 0.1 and 100 with no explanation, symbols or extra words."
            },
            {"role": "user", "content": prompt}
        ]
    )
    text = response.choices[0].message["content"].strip()
    match = re.search(r"(\d+(\.\d+)?)", text)
    return float(match.group(1)) if match else None

# -------------------- Prompt Templates --------------------
def make_user_prompt():
    return f"""
    Evaluate this dating profile's appeal in the US dating market.

    - Gender: {your_gender}
    - Interested in: {your_attraction}
    - Age: {your_age}
    - Height: {your_height_ft}'{your_height_in}"
    - Income: ${your_income}
    - Fitness: {your_fitness} workouts/week
    - Education: {your_edu}
    - Animal lover: {your_animals}
    - Has kids: {your_kids}
    - State: {your_state}
    - Attractiveness: {your_attractiveness}/10
    - MBTI: {your_mbti}

    Respond with a percentile score (0.1–100).
    """

def make_ideal_prompt():
    return f"""
    Estimate how rare this ideal partner is in the US dating pool.

    - Height at least: {ideal_height_ft}'{ideal_height_in}"
    - Income at least: ${ideal_income}
    - Fitness: {ideal_fitness} workouts/week
    - Education: {ideal_edu}
    - Animal lover: {ideal_animals}
    - Has kids: {ideal_kids}
    - Attractiveness: {ideal_attractiveness}/10
    - MBTI: {ideal_mbti}

    Respond with a percentile score (0.1–100) — lower = rarer.
    """

# -------------------- Result Logic --------------------
if st.button("💘 Calculate My Love Odds"):
    with st.spinner("Crunching your odds..."):

        user_percentile = get_percentile(make_user_prompt())
        ideal_percentile = get_percentile(make_ideal_prompt())

        if not user_percentile or not ideal_percentile:
            st.error("Something went wrong with the evaluation. Try again or check your API key.")
        else:
            your_rank = 100 - user_percentile
            partner_rank = 100 - ideal_percentile
            compatibility = your_rank / 100
            P = 1 - (1 - ideal_percentile / 100) ** yearly_meet
            P_adjusted = round(P * 100 * compatibility, 2)

            st.success("🎯 Results Are In! Let’s see how delulu you are...")
            st.markdown(f"**You're in the top `{round(user_percentile, 1)}%` of daters.**")

            if your_rank >= 90:
                roast = "🦄 A literal unicorn. They’re not ready for you."
            elif your_rank >= 70:
                roast = "🌟 Main character energy with ick management issues."
            elif your_rank >= 50:
                roast = "🎭 Mid-tier hottie with room for growth."
            elif your_rank >= 30:
                roast = "📉 You’re dating-app purgatory. Swipeable but forgettable."
            elif your_rank >= 10:
                roast = "🙃 You’re someone’s type, but it’s probably not your type."
            else:
                roast = "😬 You’re... brave. Good luck out there."

            st.markdown(f"**{roast}**")
            st.markdown(f"**Your ideal partner is in the top `{round(ideal_percentile, 1)}%` rarity.**")
            st.markdown(f"**Your chance of meeting them in a year: `{P_adjusted:.2f}%`** 🎯")

            if P_adjusted > 0:
                ghost_number = max(1, int(100 / P_adjusted))
                st.markdown(f"👻 You might need to ghost roughly **{ghost_number}** people this year before one turns out to be *The One* 💁‍♀️")

            # 💘 Compatibility Conclusion
            st.markdown("---")
            if abs(your_rank - partner_rank) <= 15 and P_adjusted >= 10:
                st.success("💘 You're dreaming at your level. Statistically, this could work 💌")
            elif your_rank < partner_rank - 25 and P_adjusted < 30:
                st.warning("😵‍💫 Babe... your standards are giving ✨fictional character✨.")
            elif P_adjusted > 70:
                st.success("💘 You're either a hot commodity or just realistic. Keep going, Cupid!")
            elif P_adjusted > 30:
                st.info("🧐 You're choosy, but not delulu.")
            else:
                st.warning("📉 You might be trying too hard to outkick your coverage 💔")

            # 🧠 Tips
            st.markdown("---")
            if your_rank >= 90:
                st.markdown("💅 You're perfect. Maybe it’s your standards that need a glow-up 👀")
            elif P_adjusted >= 90:
                st.markdown("🫣 The math says yes. The vibes say... swipe wisely.")
            elif P_adjusted >= 50:
                st.markdown("📈 You're close! Just polish one thing — maybe income, looks, or vibes — and you're golden.")
            else:
                if yearly_meet < 20:
                    new_meet = min(20, yearly_meet + 5)
                    new_P = 1 - (1 - ideal_percentile / 100) ** new_meet
                    new_P_adj = round(new_P * 100 * compatibility, 2)
                    diff = round(new_P_adj - P_adjusted, 2)
                    if diff > 1:
                        st.markdown(f"🧠 If you increased your yearly interactions from {yearly_meet} to {new_meet}, your odds could improve to `{new_P_adj:.2f}%` — that’s +{diff}%!")
                else:
                    st.markdown("🧠 You’re already meeting plenty of people — maybe it’s your filters that need the adjustment 💀")
