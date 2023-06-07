import streamlit as st
import requests


API_URL = "http://localhost:9800"


def get_data(serial_number):
    # Make a request to the API to get paginated data
    response = requests.get(API_URL, params={"serial_number": serial_number})
    data = response.json()
    return data


def save_feedback(feedback):
    # Make an API call to save user's feedback
    print(feedback)
    response = requests.post(f"{API_URL}/feedback", json=feedback)
    if response.status_code == 200:
        st.success("Feedback saved successfully.")
    else:
        st.error("Failed to save feedback.")

# Helper function to format passages for better readability
def format_passages(passages):
    formatted_passages = ""
    colors = ["#f7f7f7", "#f0f0f0", "#e9e9e9", "#e2e2e2", "#dbdbdb"] # List of background colors
    for i, passage in enumerate(passages, start=1):
        # color = random.choice(colors)
        color = colors[0]
        formatted_passage = " ".join(passage.split()) + "..."
        formatted_passages += f'<div style="background-color:{color}; padding: 10px; border-radius: 5px;">Rank {i}: {formatted_passage}</div>'
    return formatted_passages


def main():
    st.title("Feedback Page")
    st.title("Question and Passage Feedback")
    initial_sl_no = 0
    question_no = st.number_input("Enter the serial number of the question you want to go", step=1, value=0)
    # if st.session_state.email_address:
        
    email_address = st.text_input("Enter your company email id")
    if email_address:
        st.session_state.email_address = email_address
    if question_no != 0:
        st.session_state.serial_number = question_no
    if "serial_number" in st.session_state:
        initial_sl_no = st.session_state.serial_number
    st.write(st.session_state)
    data = get_data(initial_sl_no)
    if data:
        for entry in data:
            st.write(f"Serial Number: {entry['Serial Number']}")
            st.subheader(f"Question: {entry['Question']}")
            # Display the ordered list of passages
            st.subheader("Passages:")

            passages_list = entry["Passages"].split(";")
            passage_id_list = list(map(int, entry["Passage IDs"].split(";")))

            checked_status_list = list(map(int, str(entry["Status"]).split(";")))
            passage_text_passage_id_mapping = {}
            for passage_text, passage_id in zip(passages_list, passage_id_list):
                passage_text_passage_id_mapping[passage_text] = passage_id
            
            checkbox_states = []
            for passage_id, passage_text in zip(passage_id_list, passages_list):
                checked_status = passage_id in checked_status_list
                checkbox_state = st.checkbox(f"{passage_id}: {passage_text}", value=checked_status)
                checkbox_states.append(checkbox_state)
            
            selected_passage_ids = []
            for i, checkbox_state in enumerate(checkbox_states):
                if checkbox_state:
                    selected_passage_id = passage_id_list[i]
                    selected_passage_ids.append(selected_passage_id)
            
            st.write("Selected options:", selected_passage_ids)

            st.subheader("Expected Answer")
            st.write(entry["Expected Answer"])

            st.subheader("LLM's Answer")
            st.write(entry["Generated Answer"])

            st.subheader("Feedback on Generated Answer")
            generated_answer_feedback = st.selectbox("Answer quality", ["Good", "Poor", "Wrong"], key="generated_answer_feedback")
            remark_options = ["Verbose", "Impressive", "Succinct", "Hallucinating", "Others"]
            st.subheader("Remark on the answer characteristics")
            remark = st.selectbox("Answer characteristics", remark_options, key="remark`")

            if remark == "Others":
                remark = st.text_input("Enter your remark")
            
            if st.button("Submit"):
                feedback = {
                    "serial_number": entry['Serial Number'],
                    "selected_passage_ids": selected_passage_ids,
                    "generated_answer_feedback": generated_answer_feedback,
                    "remark": remark,
                    "email_address": email_address
                }
                save_feedback(feedback)
            st.write("---")
        
        # button_col1, button_col2 = st.columns(2)

        # if button_col1.button("Move Previous"):
        #     initial_sl_no -= 1
        #     st.session_state.serial_number = initial_sl_no
        #     data = get_data(initial_sl_no)
        #     st.experimental_rerun()
        # if button_col2.button("Move Next"):
        #     initial_sl_no += 1
        #     st.session_state.serial_number = initial_sl_no
        #     data = get_data(initial_sl_no)
        #     st.experimental_rerun()
    else:
        st.write("No more data available")


def results_page():
    st.title("Results Screen")
    # Read the Excel file and display data
    import pandas as pd
    data = pd.read_excel("EvaluationDataset.xlsx")  # Replace "your_file.xlsx" with your file path
    st.dataframe(data)


if __name__ == "__main__":
    if "serial_number" not in st.session_state:
        st.session_state.serial_number = 0
    if "email_address" not in st.session_state:
        st.session_state.email_address = ""
    page = st.sidebar.selectbox("Select Page", ["Main Page", "Results Screen"])
    
    if page == "Main Page":
        main()
    elif page == "Results Screen":
        results_page()