*** Settings ***
Documentation     End-to-end tests for the User Authentication Flow
Library           SeleniumLibrary
Library           String

*** Variables ***
${SERVER}         http://127.0.0.1:5000
${BROWSER}        Chrome
${DELAY}          0.5
${USER_FULL_NAME}      Test User
${TEST_PASSWORD}  TestPassword123

*** Test Cases ***
User Can Sign Up
    [Documentation]    Test that a new user can successfully sign up
    ${random_str}=    Generate Random String    6    [LOWER]
    Set Suite Variable    ${TEST_EMAIL}    testuser_${random_str}@example.com
    
    Open Browser To Home Page
    Click Link    class=signup-btn
    Wait Until Page Contains Element    name=name
    Input Text    name=name    ${USER_FULL_NAME}
    Input Text    name=email    ${TEST_EMAIL}
    Input Text    name=password    ${TEST_PASSWORD}
    Input Text    name=confirm    ${TEST_PASSWORD}
    Submit Form
    # After successful signup, it should redirect to login page
    Wait Until Page Contains Element    name=email
    Location Should Be    ${SERVER}/login

User Can Log In
    [Documentation]    Test that the newly created user can log in
    # Currently on login page from the previous test case
    Wait Until Page Contains Element    name=email
    Input Text    name=email    ${TEST_EMAIL}
    Input Text    name=password    ${TEST_PASSWORD}
    Press Keys    name=password    RETURN
    # After successful login, it should redirect to home page
    Wait Until Page Contains Element    class=user-name
    Element Should Contain    class=user-name    ${USER_FULL_NAME}
    Location Should Be    ${SERVER}/

User Can Log Out
    [Documentation]    Test that the logged-in user can log out
    Click Link    class=logout-btn
    # After logout, should be redirected to home page and see the login button
    Wait Until Page Contains Element    class=login-btn
    Location Should Be    ${SERVER}/
    [Teardown]    Close Browser

*** Keywords ***
Open Browser To Home Page
    Open Browser    ${SERVER}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
