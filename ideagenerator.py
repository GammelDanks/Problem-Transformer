import openai
import streamlit as st

# Streamlit App UI
st.title("Innovative Solution Generator")

st.write("This tool helps you generate innovative, technology-based solutions for your problem.")

# Retrieve the OpenAI API Key from Streamlit secrets
openai_api_key = st.secrets["general"]["OPENAI_API_KEY"]

# Set the OpenAI API key
openai.api_key = openai_api_key


# Function to generate innovative solutions
def generate_innovative_solutions(problem_description, target_audience):
    prompt = f"""
    You are an expert in innovation and technology. Given the following problem and the target audience, suggest five innovative, technology-based solutions. Describe each solution in detail, focusing on the specific technology, how the product, software, or service would work, and what it would look like.

    Problem: {problem_description}
    Target Audience: {target_audience}

    Provide five different solutions with detailed descriptions for each:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a leading expert in innovation and technology, focusing on developing new products, software, services, and processes."},
            {"role": "user", "content": prompt}
        ]
    )

    solutions = response.choices[0].message['content']
    return solutions

# Input: Problem Description
problem_description = st.text_area(
    "Describe the problem:",
    placeholder="What is the problem?",
    help="Describe the problem you want to solve."
)

# Input: Target Audience
target_audience = st.text_area(
    "Who has the problem?",
    placeholder="Who is affected by this problem?",
    help="Describe the group or individuals who are affected by the problem."
)

# Button to generate solutions
if st.button("Generate Solutions"):
    if problem_description and target_audience:
        try:
            solutions = generate_innovative_solutions(problem_description, target_audience)
            st.subheader("Innovative Solutions")
            st.write(solutions)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter both the problem description and target audience to generate solutions.")

