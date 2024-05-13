from tools_json import price_calc_json
from OpenAI_Sec import price_calc_asst_id
from functions import Best_Price_Calculator
import time

# Prebuilt assistant is used, incase unavailable, it creates a new assistant
def create_or_retrieve_assistant(client):
    try:
        assistant = client.beta.assistants.retrieve(price_calc_asst_id)
    except:
        assistant = client.beta.assistants.create(
            name="best price calc tool"
            ,instructions="""
                As a financial assistant, you help user in lowering the cost of the product that a user wants to buy by analysing loan creteria, savings, emi capacity and investment options.
                Additionally, you evaluate the user's risk tolerance.
                Use the given tools
                Provide all information to the user in integer format.
                """
            ,model="gpt-4-turbo"
            ,tools=price_calc_json
            )
    return assistant

# Initiating a new thread to keep history of the conversation
def create_thread(client):
    thread = client.beta.threads.create()
    return thread

# Taking user input and initiating run
def user_message(client, thread, user_message, assistant):
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content = user_message
    )
    return create_run(client,thread,assistant)

# Function to initiate run
def create_run(client,thread,assistant):
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    return run

def run_status_check(client,run,thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        time.sleep(0.5)

    if run.status == "requires_action":
        tool_outputs = []
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            tool_call_id = tool_call.id
            #name = tool_call.function.name
            arguments_dict = eval(tool_call.function.arguments)
            output = Best_Price_Calculator(arguments_dict)
            tool_outputs.append({"tool_call_id": tool_call_id, "output": output})

        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
        return run_status_check(client,run,thread)
    
    if run.status == "completed":
        return 'completed'
    