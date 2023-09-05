import os
import openai
import google.generativeai as palm


def main():
    #result = CallChatGPT("Make python helloworld program")
    #result = CallPalm2("Make python helloworld program")
    Call("Make python helloworld program", "Palm2")


def Call(projectDescription, LLMName, key=None):
    if LLMName == "ChatGPT":
        return CallChatGPT(projectDescription)
    elif LLMName == "Palm2":
        return CallPalm2(projectDescription, key)


def CallChatGPT( projectDescription):
    try:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
            messages = [
        {
        "role": "user",
        "content": f"{projectDescription}",
        }
        ],
        temperature=0.6,
        max_tokens=3000,
        )
      # Extract the GPT response string
        gpt_response_string = response['choices'][0]['message']['content']
        return gpt_response_string
    except Exception as e:
        print(e.message)

def CallPalm2(projectDescription, key):
            
    try:
        palm.configure(api_key=os.getenv("Palm2APIKey"))
    except Exception as e:
        print('something was wrong when trying to connect to the api', e)
    """else:
        try:
            palm.configure(api_key=str(key))
        except Exception as e:
            print(key)
            print('something was wrong when trying to connect to the api', e)"""
        
    prompt = f"""{projectDescription}"""
    response = palm.generate_text(
        model= 'models/text-bison-001',
        temperature= 0.7,
        candidate_count= 1,
        top_k= 40,
        top_p= 0.95,
        max_output_tokens= 4024,
        stop_sequences= [],
        safety_settings= [{"category":"HARM_CATEGORY_DEROGATORY","threshold":1},{"category":"HARM_CATEGORY_TOXICITY","threshold":1},{"category":"HARM_CATEGORY_VIOLENCE","threshold":2},{"category":"HARM_CATEGORY_SEXUAL","threshold":2},{"category":"HARM_CATEGORY_MEDICAL","threshold":2},{"category":"HARM_CATEGORY_DANGEROUS","threshold":2}],
        prompt = prompt
    )
    
    """response = palm.generate_text(
    **defaults,
    prompt=prompt
    )"""
    print('this the prompt', prompt)
    print('this is the unique result', response.result)
    print('this is the entire result', response)
    return response.result


if __name__ == "__main__":
    main()

