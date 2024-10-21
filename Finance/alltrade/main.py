import streamlit as st

def main():
    # Use sidebar for radio button navigation
    with st.sidebar:
        sub_apps = ["Sub App 1", "Sub App 2"]
        selected_app = st.radio("Choose a sub-app", sub_apps)

    # Display the selected sub-app in the main screen
    if selected_app == "Sub App 1":
        import sub_app1.app as sub_app1_module
        sub_app1_module.run_sub_app1()
    elif selected_app == "Sub App 2":
        import sub_app2.app as sub_app2_module
        sub_app2_module.run_sub_app2()

if __name__ == "__main__":
    main()