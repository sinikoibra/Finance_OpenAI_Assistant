import numpy as np
import regex as re

class verification_functions:

    param_dict = {
        'cost':None,
        'Loan_interest_rate':None,
        'max_tenure':None,
        'Investment_interest_rate':None,
        'savings':None,
        'min_downpayment':None,
        'emi_limit':None

        }

    param_desc_dict = {
        'cost':'value for cost of the product that he wants to buy.',
        'Loan_interest_rate':'value for interest rate per annum at which the bank is providing the loan.',
        'max_tenure':'value for maximum tenure for which the bank is ready to give the loan.',
        'Investment_interest_rate':'information regarding what kind of investments he usually makes e.g. fd, gold, bonds, equities, real estate',
        'savings':'value for amount that is saved for buying the product.',
        'min_downpayment':'value for minimum downpayment percentage that the user needs to make for buying the product.',
        'emi_limit':'value for emi paying capacity of the user e.g. monthly at max he can pay ₹6000 as emi.'
    }

    is_issue=0
    issue=[]

    def __init__(self, args_dict):
        if args_dict is None:
            raise ValueError("User input not provided")
        self.args_dict=args_dict


    def get_args_from_tool(self):
        empty_parm=[]
        for key in self.param_dict.keys():
            if key in self.args_dict and self.args_dict[key] is not None:
                self.param_dict[key]=self.args_dict[key]
            else:
                empty_parm.append(key)
        if empty_parm:
            self.is_issue = 1
            for parameters in empty_parm:
                self.issue.append(f"User has not provided {self.param_desc_dict[parameters]}")

    def emi_limit_check(self):

        if self.param_dict['cost'] and self.param_dict['min_downpayment'] and self.param_dict['Loan_interest_rate'] and self.param_dict['max_tenure'] and self.param_dict['emi_limit']:

            min_down_pymnt_amt=self.param_dict['min_downpayment']*0.01*self.param_dict["cost"]

            min_emi = credit_functions.calculate_loan_amount(self.param_dict['cost']-min_down_pymnt_amt,self.param_dict['Loan_interest_rate'],self.param_dict['max_tenure'])/(self.param_dict['max_tenure']*12)

            if min_emi>self.param_dict['emi_limit']:
                self.is_issue = 1
                self.issue.append(f"Inform the user emi paying capacity should be greater than ₹{min_emi}.")

    def savings_check(self):
        if self.param_dict['min_downpayment'] and self.param_dict["cost"] and self.param_dict['savings']:
            min_down_pymnt_amt=self.param_dict['min_downpayment']*0.01*self.param_dict["cost"]

            # savings is less than the minimum downpayment
            if self.param_dict['savings'] < min_down_pymnt_amt:
                self.is_issue = 1
                self.issue.append(f"Inform the user the savings of ₹{self.param_dict['savings']} is less than the minimum downpayment of ₹{min_down_pymnt_amt}.")

            # savings is more than the cost of the product
            if self.param_dict['savings'] > self.param_dict['cost']:
                self.is_issue = 1
                self.issue.append(f"Inform the user the savings of ₹{self.param_dict['savings']} is more than the cost of the product he doesn't need a loan.")

    # there needs to be another value checker function which will check if the values are within the limit like
    # minimum downpayment % is below 100 
    # returns are not exorbitant

    def result(self):
        self.is_issue=0
        self.issue=[]
        self.get_args_from_tool()
        self.emi_limit_check()
        self.savings_check()

        if self.is_issue:
            return 1,self.issue
        else:
            return 0,self.param_dict


class credit_functions:

    @staticmethod
    def calculate_investment_return(lumpsum, investment_return_rate, investment_tenure):
        """
        Calculating final return from the money invested
        """
        total_return = lumpsum * (1 + (investment_return_rate / 100)) ** investment_tenure
        return total_return

    @staticmethod
    def calculate_loan_amount(principal, annual_interest_rate, loan_tenure_years):
        """
        Calculating final loan amount
        """
        # Convert annual interest rate to monthly interest rate
        monthly_interest_rate = annual_interest_rate / 12 / 100
        loan_tenure_months = loan_tenure_years * 12

        # Calculate EMI using the loan EMI formula
        emi = (principal * monthly_interest_rate * (1 + monthly_interest_rate) ** loan_tenure_months) / ((1 + monthly_interest_rate) ** loan_tenure_months - 1)

        # Calculate total loan amount (EMI * number of months)
        total_loan_amount = emi * loan_tenure_months
        return total_loan_amount

    @staticmethod
    def cost_function(cost, annual_interest_rate, tenure_years, investment_return_rate, savings, savings_percentage, emi_limit):
        """
        Gives the cost of the product for current value of the tenure years and savings percentage
        """
        # Calculate principal amount for the loan
        principal = cost - (savings * (savings_percentage / 100))

        # Calculate lumpsum amount
        lumpsum = savings * (1 - (savings_percentage / 100))

        # Calculate loan amount using the provided function
        loan_amt = credit_functions.calculate_loan_amount(principal, annual_interest_rate, tenure_years)

        # Calculate investment return using the provided function
        invst_return = credit_functions.calculate_investment_return(lumpsum, investment_return_rate, tenure_years)

        # Calculate final cost
        final_cost = savings - (savings - loan_amt - lumpsum - (savings * (savings_percentage / 100)) + invst_return)

        # Check if loan EMI exceeds the limit
        if (loan_amt / (tenure_years * 12)) > emi_limit:
            final_cost = final_cost + (final_cost * 0.1)

        # Check if loan tenure exceeds the limit
        if (loan_amt / (emi_limit * 12)) > tenure_years:
            final_cost = final_cost * 0

        # Check if investment lumpsum is greater than ₹100 or 0
        if lumpsum<100 and lumpsum>0:
            final_cost = final_cost * 0


        return final_cost,lumpsum

    @staticmethod
    def final_cost_function(cost, Loan_interest_rate, max_tenure, Investment_interest_rate, savings, min_downpayment, emi_limit):
        """
        gives the lowest value of the product after considering all scenarios
        """

        min_savings_percentage = (cost / savings) * min_downpayment
        min_tenure=1

        tenure_years = np.arange(min_tenure, max_tenure + 1, 1)
        savings_percentage = np.round(np.arange(min_savings_percentage, 100.1, 0.1),1)

        curr_min_cost = 10**99
        curr_min_tenure = 0
        curr_min_savings_percentage = 0

        curr_min_cost_no_invest = 10**99
        curr_min_tenure_no_invest = 0
        curr_min_savings_percentage_no_invest = 0

        x, y = np.meshgrid(tenure_years, savings_percentage)
        for X,Y in zip(x.ravel(), y.ravel()):
            curr_cost,investment_lumpsum = credit_functions.cost_function(cost, Loan_interest_rate, X, Investment_interest_rate, savings, Y, emi_limit)
            if curr_cost != 0 and curr_cost < curr_min_cost:
                curr_min_cost = curr_cost
                curr_min_tenure = X
                curr_min_savings_percentage = Y

            if curr_cost != 0 and curr_cost < curr_min_cost_no_invest and investment_lumpsum == 0:
                curr_min_cost_no_invest = curr_cost
                curr_min_tenure_no_invest = X
                curr_min_savings_percentage_no_invest = Y

        output_dict={"final_cost":curr_min_cost,
                     "final_tenure":curr_min_tenure,
                     "final_savings_percent_fr_downpymnt":curr_min_savings_percentage,
                     "final_cost_no_invest":curr_min_cost_no_invest,
                     "final_tenure_no_invest":curr_min_tenure_no_invest}

        return output_dict

    def result(self,param_dict):

        credit_func_output_dict = credit_functions.final_cost_function(**param_dict)

        final_downpymnt_amt=credit_func_output_dict["final_savings_percent_fr_downpymnt"]*0.01*param_dict["savings"]

        EMI = credit_functions.calculate_loan_amount(param_dict["cost"] - final_downpymnt_amt,param_dict["Loan_interest_rate"],credit_func_output_dict["final_tenure"])/(credit_func_output_dict["final_tenure"]*12)

        if credit_func_output_dict["final_cost_no_invest"] <= credit_func_output_dict["final_cost"]:
            output_str = f"""
            At the current savings of ₹{param_dict["savings"]} and maximum EMI paying capacity of ₹{param_dict["emi_limit"]} the user won't have enough to invest.
            So he should give entire savings as downpayment and take loan for the rest for a tenure of {credit_func_output_dict["final_tenure_no_invest"]} years
            Finally he has to pay  ₹{credit_func_output_dict["final_cost_no_invest"]} at an EMI of ₹{EMI}
            """
        else:
            output_str=f"""
            The lowest price at which user can buy the product is ₹{credit_func_output_dict["final_cost"]} \n
            let me explain how \n
            - Instead of giving entire savings as downpayment, user should make a downpayment of ₹{final_downpymnt_amt} \n
            - After making the downpayment user should take a loan for the remaining amount , which is ₹{param_dict["cost"]-final_downpymnt_amt} at an interest rate of
            {param_dict["Loan_interest_rate"]}% (defined by user) for a tenure of {credit_func_output_dict["final_tenure"]} years. The EMI will be equal to ₹{EMI} \n
            - After making the downpayment user will be left with savings of ₹{param_dict["savings"] - final_downpymnt_amt} which needs to be invested for the same tenure of {credit_func_output_dict["final_tenure"]} years at a return rate of {param_dict["Investment_interest_rate"]}% (this value is chosen as per user's risk taking capacity)

            In case the user choses not to invest and to give the entire savings as downpayment and take loan for the rest of the amount of ₹{param_dict["cost"]-param_dict["savings"]} for a tenure of {credit_func_output_dict["final_tenure_no_invest"]} years
            then the product will cost him ₹{credit_func_output_dict["final_cost_no_invest"]}

            Finally by investing and taking a larger loan the user will save around ₹{credit_func_output_dict["final_cost_no_invest"] - credit_func_output_dict["final_cost"]}

            If the user wants lower cost for the product than the user can try to increase the savings amount or emi paying capacity
            """
        return output_str
    

def Best_Price_Calculator(args_dict):
    if 'Investment_interest_rate' in args_dict.keys():

        pattern = "^\w+"
        string=args_dict['Investment_interest_rate']
        risk_tolerance=re.search(pattern, string).group()

        if risk_tolerance == "high":
            args_dict['Investment_interest_rate']=13.5
        elif risk_tolerance == "moderate":
            args_dict['Investment_interest_rate']=10
        elif risk_tolerance == "low":
            args_dict['Investment_interest_rate']=7
        else:
            args_dict['Investment_interest_rate'] = None
         
            
            
    is_issue,output = verification_functions(args_dict).result()

    if is_issue:
        return '\n'.join(output)
    else:
        return credit_functions().result(args_dict)


