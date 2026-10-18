*** Settings ***
Documentation     RPA Bot to analyze and score Rental Applications based on AI limit
Library           SeleniumLibrary
Library           ../libraries/RentalAnalyzer.py

*** Variables ***
${SERVER}         http://127.0.0.1:5000
${BROWSER}        Chrome
${DELAY}          0.5
${USER_EMAIL}     user@gamil.com
${USER_PASS}      user123
${TASK_PARAM}     75

*** Test Cases ***
Seller Auto Approve
    [Documentation]    Bot logs into Seller Dashboard, scores pending apps, and approves them based on user limit.
    ${options}=    Set Variable    add_argument("--disable-popup-blocking"); add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False, "profile.password_manager_leak_detection": False})
    Open Browser    ${SERVER}/login    ${BROWSER}    options=${options}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    
    # Seller Login
    Wait Until Page Contains Element    name=email
    Input Text    name=email    ${USER_EMAIL}
    Input Text    name=password    ${USER_PASS}
    Submit Form
    
    # Navigate to Seller Dashboard
    Go To    ${SERVER}/dashboard/seller
    
    # Check if there is any Pending application
    ${pending_count}=    Get Element Count    xpath=//div[@id='tab-new']//tr[.//option[@selected and @value='Pending']]
    FOR    ${i}    IN RANGE    ${pending_count}
        Process First Pending Application
    END
    
    # Switch to Processed Tab to verify
    Wait Until Page Contains Element    xpath=//*[self::a or self::button][contains(text(), 'Processed Applications')]
    Click Element    xpath=//*[self::a or self::button][contains(text(), 'Processed Applications')]
    Wait Until Element Is Visible    xpath=//div[@id='tab-processed']
    
    Close Browser

*** Keywords ***
Process First Pending Application
    # Find the row containing a Pending dropdown
    ${row_xpath}=    Set Variable    xpath=(//tr[.//option[@selected and @value='Pending']])[1]
    
    # Extract values
    ${applicant_name}=    Get Text    ${row_xpath}//td[1]//strong
    ${applicant_cell}=    Get Text    ${row_xpath}//td[1]
    ${property_title}=    Get Text    ${row_xpath}//td[2]//strong
    ${emp_status}=    Get Text    ${row_xpath}//span[@class='app-emp-status']
    ${monthly_income}=    Get Text    ${row_xpath}//span[@class='app-income']
    ${rent_amount}=    Get Text    ${row_xpath}//span[@class='rent-amount']
    
    # Call our Python AI logic
    ${score}=    Calculate Suitability Score    ${emp_status}    ${monthly_income}    ${rent_amount}
    
    # Update the UI score (this inputs the full string like "Score: 8/10 (Reason)")
    Input Text    ${row_xpath}//input[@name='ai_suitability_score']    ${score}
    
    # Extract the numeric part (e.g. 8 from "Score: 8/10") and convert to percentage
    ${percentage_score}=    Evaluate    int(re.search(r'Score: (\\d+)', '''${score}''').group(1)) * 10 if re.search(r'Score: (\\d+)', '''${score}''') else 0    re
    
    # If the AI Score percentage is greater than or equal to the User's TASK_PARAM, auto approve!
    ${decision}=    Set Variable If    ${percentage_score} >= ${TASK_PARAM}    Approved    Rejected
    Select From List By Value    ${row_xpath}//select[@name='status']    ${decision}
    
    # Submit the decision
    Click Button    ${row_xpath}//button[@type='submit']
