import streamlit as st
import requests

base_url='http://127.0.0.1:8000/'


if "token" not in st.session_state:
    st.session_state.token = None

sel=st.selectbox("Select:",['register','login'])
if sel == 'register':
  st.header('Fill form')
  username=st.text_input("enter username")
  email=st.text_input("enter email id")
  password=st.text_input("enter password",type='password')
  submit=st.button('submit')
  if username and email and password and submit:
    res=requests.post(f'{base_url}/register',json={'username':username,'email':email,'password':password})
    st.write(res.text)


elif sel == 'login':
    st.header("Input Details")
    username = st.text_input("Please enter your username")
    password = st.text_input("Please enter your Password", type='password')

    if username and password:
        resp=requests.post(f'{base_url}/token',data={"username":username,'password':password})
        if resp.status_code==200:
            st.write("Login Successful")
            data=resp.json()
            st.session_state.token=data['access_token']
        else: st.write("Invalid username and password")

    if st.session_state.token:
        st.header('fetch data')
        ques=st.text_input("enter question")
        headers={'Authorization':f'Bearer {st.session_state.token}'}
        resp2=requests.get(f'{base_url}/detail_s',headers=headers,params={'ques':ques})
        dat=resp2.json()
        st.write(dat['Ai_res'])