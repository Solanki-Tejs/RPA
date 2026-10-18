*** Settings ***
Documentation     RPA Bot to analyze and score Rental Applications
Library           SeleniumLibrary
Library           ../libraries/RentalAnalyzer.py
Library           OperatingSystem

*** Variables ***
${SERVER}         http://127.0.0.1:5000
${BROWSER}        Chrome
${DELAY}          0.5

*** Test Cases ***
Step 1: Tenant Submits Application
    [Documentation]    Simulates a tenant applying for rent so the RPA bot has data to process.
    Open Browser    ${SERVER}/login    ${BROWSER}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    
    # Login as tenant
    Wait Until Page Contains Element    name=email
    Input Text    name=email    testuser2@example.com
    Input Text    name=password    TestPassword123
    Submit Form
    
    # Go to rent page
    Go To    ${SERVER}/rent
    
    # Click the first property's "View Details"
    Wait Until Page Contains Element    xpath=//a[contains(@class, 'view-btn')]
    ${rent_details_url}=    Get Element Attribute    xpath=(//a[contains(@class, 'view-btn')])[1]    href
    Go To    ${rent_details_url}
    
    # Click Apply for Rent
    Wait Until Page Contains Element    xpath=//a[contains(@href, '/apply_rent/')]
    ${apply_url}=    Get Element Attribute    xpath=//a[contains(@href, '/apply_rent/')]    href
    Go To    ${apply_url}
    
    # Fill Application Form
    Wait Until Page Contains Element    name=applicant_name
    Input Text    name=applicant_name    RPA Test Tenant
    Input Text    name=email    tenant@example.com
    Input Text    name=phone    +91 99999 88888
    
    Select From List By Value    name=employment_status    Employed
    Input Text    name=monthly_income    80000
    Input Text    name=message    Hello, please process my application.
    
    # Create dummy files to upload
    Create Dummy Files
    Choose File    name=identity_doc    ${CURDIR}/dummy_id.pdf
    Choose File    name=income_proof_doc    ${CURDIR}/dummy_income.pdf
    Choose File    name=bank_statement_doc    ${CURDIR}/dummy_bank.pdf
    
    # Submit
    Submit Form
    
    # Verify redirected back to property details
    Wait Until Page Contains Element    xpath=//h3[contains(text(), 'Property Description')]
    Close Browser

Step 2: RPA Bot Processes Application (As Seller)
    [Documentation]    Bot logs into Seller Dashboard, scores pending apps, and updates them.
    Open Browser    ${SERVER}/login    ${BROWSER}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    
    # Seller Login
    Wait Until Page Contains Element    name=email
    Input Text    name=email    user@gamil.com
    Input Text    name=password    user123
    Submit Form
    
    # Navigate to Seller Dashboard
    Go To    ${SERVER}/dashboard/seller
    
    # Check if there is any Pending application
    ${pending_count}=    Get Element Count    xpath=//div[@id='tab-new']//tr[.//option[@selected and @value='Pending']]
    Run Keyword If    ${pending_count} > 0    Process First Pending Application
    
    # Switch to Processed Tab to verify
    Wait Until Page Contains Element    xpath=//*[self::a or self::button][contains(text(), 'Processed Applications')]
    Click Element    xpath=//*[self::a or self::button][contains(text(), 'Processed Applications')]
    Wait Until Page Contains Element    xpath=//div[@id='tab-processed']//tr[.//option[@selected and @value='AI Reviewed']]
    
    Close Browser

*** Keywords ***
Login As Buyer And Return To Apply
    # Using the user created in previous auth_flow.robot or sign up on the spot
    Input Text    name=email    testuser2@example.com
    Input Text    name=password    TestPassword123
    Submit Form
    # After login it goes to Home. We must navigate back to rent and apply.
    Go To    ${SERVER}/rent
    Wait Until Page Contains Element    xpath=//a[contains(@class, 'view-btn')]
    Click Link    xpath=(//a[contains(@class, 'view-btn')])[1]
    Wait Until Page Contains Element    xpath=//a[contains(@href, '/apply_rent/')]
    ${apply_url}=    Get Element Attribute    xpath=//a[contains(@href, '/apply_rent/')]    href
    Go To    ${apply_url}

Process First Pending Application
    # Find the row containing a Pending dropdown
    ${row_xpath}=    Set Variable    xpath=(//tr[.//option[@selected and @value='Pending']])[1]
    
    # Extract values
    ${emp_status}=    Get Text    ${row_xpath}//span[@class='app-emp-status']
    ${monthly_income}=    Get Text    ${row_xpath}//span[@class='app-income']
    ${rent_amount}=    Get Text    ${row_xpath}//span[@class='rent-amount']
    
    # Call our Python AI logic
    ${score}=    Calculate Suitability Score    ${emp_status}    ${monthly_income}    ${rent_amount}
    
    # Update the UI
    Input Text    ${row_xpath}//input[@name='ai_suitability_score']    ${score}
    Select From List By Value    ${row_xpath}//select[@name='status']    AI Reviewed
    Click Button    ${row_xpath}//button[@type='submit']

Create Dummy Files
    # Create empty PDF files to use for the upload fields
    Create File    ${CURDIR}/dummy_id.pdf
    Create File    ${CURDIR}/dummy_income.pdf
    Create File    ${CURDIR}/dummy_bank.pdf
