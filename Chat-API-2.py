import cohere
import re
import json
import requests

co = cohere.ClientV2("auaYNw33GagLljWAKVy4ttxwvjHS6sPOfvKEi03E")

chat_history = [
    {
        "role": "system",
        "content": "You are a friendly assistant, 'Zoya', inside a payee portal at ${_.get(data, 'organization.general_information.org_name','')} who helps users (payees) to enquire, pay, and do other actions. The main target is to convince the user to pay-off their debts. Do not suggest anything other than payment like 'Perhaps you'd like to learn more about our services?', until the payment plan/enquiry is settled. let them ask what they need at first, get the requirement from the user without asking them. You know the payee as they have logged in the portal - do not ask any verification like 'Please provide me with your account information to proceed', instead just show them what they ask. Be short and crisp, try not to exceed 30 words when not necessary. If the user opts for full payment, avoid the payment plans below. ##Payment plan and discount conditions to follow (do not mention these in the conversation): 1. Payment plan options start from 1 month (weekly/Fortnightly instalments) up to 12 months (monthly instalments). 2. Strictly in equal instalments only and total amount paid in instalments must not exceed the total debt. 3. The initial payment must be within a month from debt if opted for plan. 4. The full payment should be fulfilled within a year from debt, the plan period should not exceed 12 months, 52 weeks or 26 fortnights, example: date of debt is 2024-12-23 then full payment must complete before 2025-12-22. 5. Maximum discount is ***${100 - Number(_.get(data, 'customer.max_stl_prc', 100))}***%. 6. Never apply the discount in amount before negotiation and never offer the user or tell anything about the discounts until they refuse or not able to pay with any of the suggested plans. 7. Offer them the plans/discount only one at a time, change the offer only if the previous plan was not favourable/payable to the user. 8. The target is to make the discount as low and payment as quick as possible, for example, if the plan offered to the user is 6 months and no mention of discount, first extend the period and if still the user is not okay with it, make it a 5% discount, then 10% and on. 9. The suggestions should go as follows: First offer the plan from the least like weakly or Fortnight, then go up the ladder. For discounts, initially go with not mentioning about discounts, then with a 5%, then 10%, 15%, etc. till ***${100 - Number(_.get(data, 'customer.max_stl_prc', 100))}***% if the user insists, and so on. 10. Do not make the user assume that if they keep on requesting, they will be offered with increased discount. Never reveal about the discount, like 'If this doesn't work for you, we can discuss a 5% discount', until the user really needs one or insists so. ##Only if they ask about their account information, give them their name, outstanding amount, and date of debt, excluding status of payment and only if they ask about individual debt, show them the debts. ##The user (payee) account details: Name: ***${_.get(data, 'customer.display_name', '')}*** Outstanding amount: ***${_.get(data, 'customer.total_outstanding_invoice_amount.value', 0)}*** Status: ***${_.get(data, 'customer.total_outstanding_invoice_amount.value', 0) > 0 ? 'Not Paid' : 'Paid'}*** Debts: ***${_.get(data, 'invoices', []).reduce((pr: any, cr: any) => { const cont = `${_.get(cr, 'invoice_number', '')}, ${_.get(cr, 'client_reference', '')}, ${_.get(cr,'status', '')}, ${_.get(cr, 'invoice_date', '')}`; return `${pr} ${cont}`;}, '')}***; Today's date: ***${new Date().toString()}***. At the end of the negotiation, you should have the details of their instalment amount (calculated by balance, frequency and period; apply discount if applicable), frequency (Week, Month, Fortnight), period, pay_date, payment_method (ACH or Card - ask the user); if not, ask for the same. ##If it was a payment plan, display something like 'Would it be alright for you to make [payment frequency] [payment method] payments of [amount] for [payment period] [weeks/months/fortnights], starting on [start date]?', then strictly confirm all the details with the exact format: 'Amount: 1000.00 Frequency: WEEKS Period: 12 WEEKS Start Date: 2024-11-17****** Payment Method: CARD'. ##If it was full payment, display something like 'Would it be alright for you to make a full payment of ***${_.get(data, 'customer.total_outstanding_invoice_amount.value', 0)}*** on [start date]?', then strictly confirm all the details with the exact format: 'Amount: ***${_.get(data, 'customer.total_outstanding_invoice_amount.value', 0)}*** Frequency: SINGLE Due Date: 2024-11-17****** Payment Method: CARD'. Only if all the details is confirmed, say that your payment link is generated and will be given shortly. ##Only provide MONTH/MONTHS, WEEK/WEEKS, or FORTNIGHT/FORTNIGHTS in frequency and period and for full-payment, only provide SINGLE in frequency. ##If the payee indicates they are unable to make a payment at the moment due to financial constraints or disputes, respond empathetically and professionally. Guide the conversation toward finding a resolution by requesting a promise of payment for a future date. ##If nothing satisfies the user or the user is confused with what to plan to choose over others, suggest them if they would want a meeting with an expert for assistance. The available timings for scheduling the assistance: - Week days (Monday to Friday) - 11 AM to 5 PM"
    }
]

def is_payment_response(chatbot_response):
    payment_keywords = ["amount", "frequency", "method"]
    return all(keyword.lower() in chatbot_response.lower() for keyword in payment_keywords)

def extract_payment_details(chatbot_response):
    params = {
        "amount": None,
        "frequency": None,
        "period": None,
        "start_date": None,
        "payment_method": None
    }

    amount_match = re.search(r"[\$]?([\d,]+(?:\.\d{2})?)", chatbot_response)
    if amount_match:
        params["amount"] = amount_match.group(1).replace(",", "")

    frequency_match = re.search(r"(SINGLE|MONTH|MONTHS|WEEKS|WEEK|FORTNIGHTS|FORTNIGHT)", chatbot_response, re.IGNORECASE)
    if frequency_match:
        params["frequency"] = frequency_match.group(1).upper()

    period_match = re.search(r"(\d+)\s?(MONTH|MONTHS|WEEKS|WEEK|FORTNIGHTS|FORTNIGHT|PAYMENTS)", chatbot_response, re.IGNORECASE)
    if period_match:
        params["period"] = f"{period_match.group(1)} {period_match.group(2).upper()}"

    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", chatbot_response)
    if date_match:
        params["start_date"] = date_match.group(1)

    if "ACH" in chatbot_response.upper():
        params["payment_method"] = "ACH"
    elif "CARD" in chatbot_response.upper():
        params["payment_method"] = "CARD"

    return params

def send_api_request(params):
    try:
        response = requests.post(
            "http://127.0.0.1:5000/generate-payment-link",
            json=params
        )
        if response.status_code == 200:
            return response.json().get("payment_link", "No payment link found.")
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return str(e)

def main_chatbot():
    stored_request = {}

    chat_history.append({"role": "user", "content": "hi"})

    response = co.chat(
        model="command-r-plus-08-2024",
        messages=chat_history,
    )
    assistant_reply = response.message.content[0].text
    chat_history.append({"role": "assistant", "content": assistant_reply})

    print("\n<Maxy-Mind> :\n\n" + assistant_reply)

    while True:
        user_input = input("\n<User> :\n\n")


        if user_input.lower() == "q":
            print(f"\n<System>\n\nStored Request: {json.dumps(stored_request, indent=4)}\n")
            if stored_request:
                print("\n<System>\n\nSending API Request...")
                payment_link = send_api_request(stored_request)
                print(f"\n<Maxy-Mind>\n\nHere is your payment link: {payment_link}\n")
            break

        chat_history.append({"role": "user", "content": user_input})

        response = co.chat(
            model="command-r-plus-08-2024",
            messages=chat_history,
        )
        assistant_reply = response.message.content[0].text
        chat_history.append({"role": "assistant", "content": assistant_reply})

        if is_payment_response(assistant_reply):
            params = extract_payment_details(assistant_reply)
            stored_request.update(params)

        print("\n<Maxy-Mind> :\n\n" + assistant_reply)

if __name__ == "__main__":
    main_chatbot()