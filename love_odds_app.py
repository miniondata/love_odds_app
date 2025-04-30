import streamlit as st
from openai import OpenAI
import math
import re

# -------------------- API Setup --------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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
st.markdown("[💡 Explore MBTI types](https://www.16personalities.com/personality-types)")

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
your_attractiveness = st.slider("Your attractiveness (1 = troll, 10 = hot hot hot)", 1, 10, 6)
your_mbti = st.text_input("Your MBTI (optional)", max_chars=4)
st.markdown("[💡 Explore MBTI types](https://www.16personalities.com/personality-types)")
yearly_meet = st.slider("How many people are you willing to meet per year?", 0, 20, 5)

# -------------------- ChatGPT Scoring --------------------
def generate_profile_context(your_gender, your_attraction):
    if your_gender == "Woman" and your_attraction == "Men":
        return "Evaluate this profile from the perspective of straight men judging a woman. Prioritize attractiveness, fitness, warmth, and lifestyle compatibility."
    elif your_gender == "Man" and your_attraction == "Women":
        return "Evaluate this profile from the perspective of straight women judging a man. Prioritize income, height, ambition, emotional maturity, and fitness."
    else:
        return "Evaluate this profile neutrally for universal dating desirability, considering common standards like attractiveness, education, fitness, and personality."

profile_context = generate_profile_context(your_gender, your_attraction)

def get_percentile(prompt):
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You're a brutally honest dating coach and data analyst for the US dating market. 
                    You evaluate profiles based on **objective desirability** (not emotional connection, personality, or vibes).
                    
                    Use these general US dating norms for calibration:
                    - Income: $100K/year = top 20%, $150K+ = top 10%, $200K+ = top 5%
                    - Height (men): 5'10"+ = top 50%, 6'0"+ = top 15%, 6'2"+ = top 5%
                    - Physical Attractiveness (1–10): 8+ = top 15%, 9+ = top 5%, 10 = top 1%
                    - Age: Under 30 = favorable for women; Under 40 = favorable for men
                    - Kids: Having children is generally a disadvantage unless stated otherwise
                    - Fitness: 3–5 workouts/week = average; 6–7 = very fit
                    
                    Return ONLY a percentile score between 0.1 and 100 (no symbols, no explanation) where:
                    - **0.1% = exceptionally desirable (elite)**
                    - **100% = lowest ranked**
                    "
                )
            },
            {"role": "user", "content": prompt}
        ]
    )
    text = response.choices[0].message.content.strip()
    match = re.search(r"(\d+(\.\d+)?)", text)
    return float(match.group(1)) if match else None

# -------------------- Prompt Templates --------------------
def make_user_prompt():
    return f"""
    Evaluate this dating profile's **objective appeal** in the US dating market.
    Use factors like physical appearance, income, education, fitness, age, and whether they have kids.

    - Gender: {your_gender}
    - Interested in: {your_attraction}
    - Age: {your_age}
    - Height: {your_height_ft}'{your_height_in}"
    - Income: ${your_income}
    - Education: {your_edu}
    - Fitness: {your_fitness} workouts/week
    - Loves animals: {your_animals}
    - Has kids: {your_kids}
    - Physical attractiveness rating (1 = troll, 10 = hot hot hot): {your_attractiveness}
    - MBTI: {your_mbti or 'Not specified'}

    Focus on physical and socioeconomic desirability, not personality, vibes, or emotional traits.
    Return ONLY a percentile score from 0.1 to 100.
    """

def make_ideal_prompt():
    return f"""
    Estimate how rare this ideal partner is in the US dating pool based on physical and socioeconomic traits.
    
    - Minimum Height: {ideal_height_ft}'{ideal_height_in}"
    - Minimum Income: ${ideal_income}
    - Education: {ideal_edu}
    - Workouts/week: {ideal_fitness}
    - Loves animals: {ideal_animals}
    - Has kids: {ideal_kids}
    - Physical attractiveness rating (1 = unattractive, 10 = model-level hot): {ideal_attractiveness}
    - MBTI: {ideal_mbti or 'Not specified'}

    Rarity is based on how common this person would be in the general population.
    Return only a number between 0.1 and 100 — **lower = rarer/more elite.**
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
            true_rank = your_rank  # now defined for tip logic
            partner_rank = 100 - ideal_percentile
            compatibility = your_rank / 100
            P = 1 - (1 - ideal_percentile / 100) ** yearly_meet
            P_adjusted = round(P * 100 * compatibility, 2)

            st.success("🎯 Results are In! Let’s see how delulu you are...")
            st.markdown(f"**You're in the top `{round(user_percentile, 1)}%` of daters.**")

            if your_rank >= 90:
                roast = "🦄 A literal unicorn. They’re not ready for you."
            elif your_rank >= 70:
                roast = "🌟 Main character energy with ick management issues."
            elif your_rank >= 50:
                roast = "🧀 Mid-tier hottie with room for growth."
            elif your_rank >= 30:
                roast = "🤳 You’re dating-app purgatory. Swipeable but forgettable."
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

            # 🧠 Tips Section
            st.markdown("---")
            
            if your_rank >= 90 and partner_rank <= 50:
                st.markdown("💅 You're perfect. Maybe it's your standards that need a glow-up 👀")
            elif P_adjusted >= 90:
                st.markdown("🫣 The math says yes. The vibes say... swipe wisely.")
            elif P_adjusted >= 50:
                st.markdown("📈 You're close! Just polish one thing — maybe income, looks, or vibes — and you're golden.")
            else:
                # 🧠 Always show suggestions if chance is low (<30%)
                if yearly_meet < 20:
                    new_meet = min(20, yearly_meet + 5)
                    new_P = 1 - (1 - ideal_percentile / 100) ** new_meet
                    new_P_adj = round(new_P * 100 * compatibility, 2)
                    diff = round(new_P_adj - P_adjusted, 2)
            
                    if diff >= 1:
                        st.markdown(
                            f"🧠 Try increasing your yearly interactions from {yearly_meet} to {new_meet} — "
                            f"your odds could improve to `{new_P_adj:.2f}%` (+{diff}%)."
                        )
                        old_ghosts = max(1, int(100 / P_adjusted))
                        new_ghosts = max(1, int(100 / new_P_adj))
                        if new_ghosts < old_ghosts:
                            st.markdown(
                                f"👻 Bonus: You might only have to ghost `{new_ghosts}` people instead of `{old_ghosts}`. "
                                f"That's progress 🫡"
                            )
                    else:
                        st.markdown(
                            f"🧠 Even with more effort, odds stay under `{new_P_adj:.2f}%`. You might need to rethink your unicorn filter 🦄"
                        )
                else:
                    st.markdown("🧠 You're already meeting plenty of people — maybe it's your filters that need adjusting 💀")
