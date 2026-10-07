class RentalAnalyzer:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def calculate_suitability_score(self, employment_status, monthly_income, rent_amount):
        """
        Calculates a basic suitability score (1-10) for a rental applicant.
        Args:
            employment_status: str (e.g. 'Employed', 'Student', 'Unemployed')
            monthly_income: str or float (e.g. '50000')
            rent_amount: str or float (e.g. '15000' or '₹15,000')
        Returns:
            str: "Score: X/10. [Reason]"
        """
        try:
            # Clean currency symbols and commas
            rent_str = str(rent_amount).replace('₹', '').replace(',', '').strip()
            income_str = str(monthly_income).replace('₹', '').replace(',', '').strip()
            
            income = float(income_str)
            rent = float(rent_str)
        except ValueError:
            return "Manual Review: Invalid Income or Rent."

        if income <= 0:
            return "Score: 1/10. No income reported."

        ratio = rent / income
        score = 10

        # Rent to income ratio deductions
        if ratio > 0.3:
            score -= 2
        if ratio > 0.4:
            score -= 3
        if ratio > 0.5:
            score -= 3 # cumulative -8 if > 0.5

        # Employment status deductions
        if employment_status == 'Student':
            score -= 2
        elif employment_status == 'Unemployed':
            score -= 4
        elif employment_status == 'Self-Employed':
            score -= 1

        score = max(1, score)
        return f"Score: {score}/10 (Rent is {int(ratio*100)}% of income)"
