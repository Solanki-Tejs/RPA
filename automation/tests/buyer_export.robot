*** Settings ***
Documentation     RPA Bot to export buyer approved applications and properties to CSV
Library           SeleniumLibrary
Library           ../libraries/RentalAnalyzer.py

*** Variables ***
${SERVER}         http://127.0.0.1:5000
${BROWSER}        Chrome
${DELAY}          0.5
${USER_EMAIL}     buyer@gmail.com
${USER_PASS}      buyer123

*** Test Cases ***
Buyer Export Approved Properties To CSV
    [Documentation]    Bot logs into Buyer Dashboard, iterates submitted applications, and exports all Approved rentals to CSV.
    ${options}=    Set Variable    add_argument("--disable-popup-blocking"); add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False, "profile.password_manager_leak_detection": False})
    Open Browser    ${SERVER}/login    ${BROWSER}    options=${options}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    
    # Buyer Login
    Wait Until Page Contains Element    name=email
    Input Text    name=email    ${USER_EMAIL}
    Input Text    name=password    ${USER_PASS}
    Submit Form
    
    # Navigate to Buyer Dashboard
    Go To    ${SERVER}/dashboard/buyer
    Wait Until Page Contains Element    xpath=//table
    
    # Initialize Buyer CSV
    Initialize Buyer Export Csv
    
    # Count rows in Buyer Applications table
    ${rows}=    Get Element Count    xpath=//table//tbody/tr
    Run Keyword If    ${rows} == 0    Log    No submitted applications found.
    
    # Iterate and export approved rows
    FOR    ${i}    IN RANGE    1    ${rows} + 1
        ${row_xpath}=    Set Variable    xpath=(//table//tbody/tr)[${i}]
        Scrape Buyer Row And Export    ${row_xpath}
    END
    
    Log    Exported approved rental applications successfully.
    Close Browser

*** Keywords ***
Scrape Buyer Row And Export
    [Arguments]    ${row_xpath}
    ${property_cell}=    Get Text    ${row_xpath}//td[1]
    ${landlord_cell}=    Get Text    ${row_xpath}//td[2]
    ${applied_on}=       Get Text    ${row_xpath}//td[3]
    ${status}=           Get Text    ${row_xpath}//td[4]
    ${score}=            Get Text    ${row_xpath}//td[5]
    
    Append Buyer Application    ${property_cell}    ${landlord_cell}    ${applied_on}    ${status}    ${score}
