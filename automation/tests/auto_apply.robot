*** Settings ***
Documentation     RPA Bot to Smart Apply for Properties across Categories (Rent, Buy, Commercial) with Filters
Library           SeleniumLibrary
Library           OperatingSystem
Library           Collections

*** Variables ***
${SERVER}             http://127.0.0.1:5000
${BROWSER}            Chrome
${DELAY}              0.5
${USER_EMAIL}         testuser2@example.com
${USER_PASS}          TestPassword123
${TASK_PARAM}         
${APPLY_CAT}          All
${APPLY_LOC}          
${APPLY_TYPE}         
${APPLY_BUDGET}       
${BUYER_NAME}         RPA Test Tenant
${BUYER_PHONE}        +91 99999 88888
${BUYER_BUDGET}       80000
${BUYER_OCCUPATION}   Employed
${BUYER_MSG}          Hello!
${BUYER_ID_DOC}       
${BUYER_INCOME_DOC}   
${BUYER_BANK_DOC}     

*** Test Cases ***
Smart Apply Process
    [Documentation]    Bot logs in as a tenant/buyer and applies for properties matching specified category and filters.
    ${options}=    Set Variable    add_argument("--disable-popup-blocking"); add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False, "profile.password_manager_leak_detection": False})
    Open Browser    ${SERVER}/login    ${BROWSER}    options=${options}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    
    # Login as tenant using credentials saved in Plotify settings
    Wait Until Page Contains Element    name=email
    Input Text    name=email    ${USER_EMAIL}
    Input Text    name=password    ${USER_PASS}
    Submit Form
    
    # Determine target category pages to search
    IF    '${APPLY_CAT}' == 'Rent'
        @{pages}=    Create List    /rent
    ELSE IF    '${APPLY_CAT}' == 'Buy' or '${APPLY_CAT}' == 'Sell'
        @{pages}=    Create List    /buy
    ELSE IF    '${APPLY_CAT}' == 'Commercial'
        @{pages}=    Create List    /commercial
    ELSE
        @{pages}=    Create List    /rent    /buy    /commercial
    END

    @{all_target_urls}=    Create List
    ${budget_to_use}=    Set Variable If    '${APPLY_BUDGET}' != ''    ${APPLY_BUDGET}    ${TASK_PARAM}
    
    FOR    ${page}    IN    @{pages}
        Go To    ${SERVER}${page}
        ${card_count}=    Get Element Count    xpath=//div[contains(@class, 'property-card')]
        IF    ${card_count} > 0
            Wait Until Page Contains Element    id=filter-budget
            Run Keyword If    '${APPLY_LOC}' != ''    Input Text    id=filter-location    ${APPLY_LOC}
            Run Keyword If    '${APPLY_TYPE}' != '' and '${APPLY_TYPE}' != 'All Types'    Run Keyword And Ignore Error    Select From List By Label    id=filter-type    ${APPLY_TYPE}
            Run Keyword If    '${budget_to_use}' != '' and '${budget_to_use}' != '0'    Input Text    id=filter-budget    ${budget_to_use}
            Click Element    id=search-btn
            Sleep    0.5s
            
            ${js}=    Catenate    SEPARATOR=\n
            ...    let urls = [];
            ...    let cards = document.querySelectorAll('.property-card');
            ...    for (let card of cards) {
            ...        if (card.style.display !== 'none' && card.offsetParent !== null) {
            ...            if (card.getAttribute('data-applied') === 'true') continue;
            ...            let btn = card.querySelector('.view-btn') || card.querySelector('.details-btn');
            ...            if (btn && btn.href) urls.push(btn.href);
            ...        }
            ...    }
            ...    return urls;
            
            ${page_urls}=    Execute Javascript    ${js}
            FOR    ${u}    IN    @{page_urls}
                Append To List    ${all_target_urls}    ${u}
            END
        END
    END
    
    ${count}=    Get Length    ${all_target_urls}
    Log    Found ${count} matching properties across category '${APPLY_CAT}' to apply for.
    
    FOR    ${url}    IN    @{all_target_urls}
        Go To    ${url}
        
        # Check if already applied or if apply button exists
        ${has_apply}=    Run Keyword And Return Status    Page Should Contain Element    xpath=//a[contains(@href, '/apply_rent/')]
        IF    ${has_apply}
            ${apply_url}=    Get Element Attribute    xpath=//a[contains(@href, '/apply_rent/')]    href
            Go To    ${apply_url}
            
            # Fill Application Form using our DB Profile Variables dynamically passed from the RPA Dashboard!
            Wait Until Page Contains Element    name=applicant_name
            Input Text    name=applicant_name    ${BUYER_NAME}
            Input Text    name=email             ${USER_EMAIL}
            Input Text    name=phone             ${BUYER_PHONE}
            
            Select From List By Value    name=employment_status    ${BUYER_OCCUPATION}
            Input Text    name=monthly_income    ${BUYER_BUDGET}
            Input Text    name=message           ${BUYER_MSG}
            
            # Upload Real Files from DB Paths
            Run Keyword If    '${BUYER_ID_DOC}' != ''    Choose File    name=identity_doc    ${BUYER_ID_DOC}
            Run Keyword If    '${BUYER_INCOME_DOC}' != ''    Choose File    name=income_proof_doc    ${BUYER_INCOME_DOC}
            Run Keyword If    '${BUYER_BANK_DOC}' != ''    Choose File    name=bank_statement_doc    ${BUYER_BANK_DOC}
            
            # Submit Application
            Submit Form
            
            # Verify redirected back to property details
            Wait Until Page Contains Element    xpath=//h3[contains(text(), 'Property Description')]
        ELSE
            Log    Skipping property at ${url}: already applied or apply button not available.
        END
    END
    
    Close Browser
