import autogen

#Use the local LLM server same as before
config_list = [
    {
        "model": "mistral-instruct-7b", #the name of your running model
        "api_base": "http://127.0.0.1:1234/v1", #the local address of the api
        "api_type": "open_ai",
        "api_key": "sk-111111111111111111111111111111111111111111111111", # just a placeholder
    }
]

# set a "universal" config for the agents
agent_config = {
    "seed": 42,  # change the seed for different trials
    "temperature": 0,
    "max_tokens": -1,
    "config_list": config_list,
    "request_timeout": 4800,
}

# humans
user_proxy = autogen.UserProxyAgent(
   name="Admin",
   system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.",
   code_execution_config=False,
)

executor = autogen.UserProxyAgent(
    name="Executor",
    system_message="Executor. Execute the code written by the engineer and report the result.",
    human_input_mode="NEVER",
    code_execution_config={"last_n_messages": 3, "work_dir": "paper"},
)

# agents
engineer = autogen.AssistantAgent(
    name="Engineer",
    llm_config=agent_config,
    system_message='''Engineer. You follow an approved plan. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
''',
)

scientist = autogen.AssistantAgent(
    name="Scientist",
    llm_config=agent_config,
    system_message="""Scientist. You follow an approved plan. You are able to categorize papers after seeing their abstracts printed. You don't write code."""
)

planner = autogen.AssistantAgent(
    name="Planner",
    system_message='''Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
The plan may involve an engineer who can write code and a scientist who doesn't write code.
Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a scientist.
''',
    llm_config=agent_config,
)

critic = autogen.AssistantAgent(
    name="Critic",
    system_message="Critic. Double check plan, claims, code from other agents and provide feedback. Check whether the plan includes adding verifiable info such as source URL.",
    llm_config=agent_config,
)

# start the "group chat" between agents and humans
groupchat = autogen.GroupChat(agents=[user_proxy, engineer, scientist, planner, executor, critic], messages=[], max_round=50)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=agent_config)

# Start the Chat!
user_proxy.initiate_chat(
    manager,
    message="""

    read json file https://raw.githubusercontent.com/olaTechie/vacTrials/main/vacTrials.json 

create a csv file for the output
summarise first five rows with the following information from below 1 to 24, 
output as a table format, 
format output neatly


information required from each row
1.	Study Identifier (NCT Number)
2.	Title (Study Title)
3.	First author: 
4.	Publication year: 
5.	Study period: 
6.	Country sites: Countries with the most running vaccine clinical trials in Africa.
7.	Trial methods of recruitment: such notices, media, advice, hospitals, etc.
8.	Settings:
9.	Study designs: clinical trials, open clinical trials, single-blind clinical trials, double-blind etc
10.	Registered clinical trials bodies: Clinicaltrials.gov, etc
11.	Clinical trials phases: phases 1, 1/2, 2, 2/3, 3, and 4.
12.	Populations studied: adults, children, adolescents, pregnant women, immunocompromised people, and people of advanced age.
13.	Interventions: parallel, single-group, and sequential assignments.
14.	Conditions studied: any African conditions for which vaccinations are utilized will be included.
15.	Vaccine name:
16.	Types of vaccines: inactivated vaccines, live-attenuated vaccines, messenger RNA (mRNA) vaccines, etc
17.	Vaccine outcomes: immunogenicity, efficacy, effectiveness, safety, delivery, and acceptability.
18.	Main limitations: 
19.	Sample size
20.	Percentage female:
21.	Proportion of loss to follow-up:
22.	Summary (main Results)
23.	Manufacturer Type
24.	Source of Funding

    
    
""",
)

# to followup of the previous question, use:
# user_proxy.send(
#     recipient=assistant,
#     message="""your followup response here""",
# )
