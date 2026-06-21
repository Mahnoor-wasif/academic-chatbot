# agent.py - Final Checklist Optimized Code
import json

# Checklist Goal and format matching descriptions
TOOL_DESCRIPTIONS = """
You are a University Academic Policy Assistant.

You MUST ALWAYS use rag_search first.

Rules:
1. Never answer from your own knowledge.
2. Always call rag_search before giving an answer.
3. Use ONLY information returned by the tools.
4. If rag_search returns no relevant policy, respond exactly:

Final Answer: I could not find this information in the university policy documents.

5. Never answer questions unrelated to university policies.
6. Never use external knowledge.

Available tools:
1. rag_search(query)
2. get_policy_by_title(title)
3. summarise_text(text)

Format:

Thought: ...
Action: tool_name
Action Input: ...
"""

def run_agent(user_question, index, model, util, groq_client, max_iterations=4):
    from tools import tool_rag_search, tool_get_policy_by_title, tool_summarise_text
    
    messages = [
        {"role": "system", "content": TOOL_DESCRIPTIONS},
        {"role": "user", "content": user_question}
    ]
    
    # ⚠️ Checklist Limit: max_iterations loops bounds are active
    for iteration in range(max_iterations):
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.0
        )
        output = response.choices[0].message.content
        messages.append({"role": "assistant", "content": output})
        
        # ⚠️ CHECKLIST REQ: Log every tool call to the terminal so you can monitor it
        print(f"\n--- [AGENT STEP {iteration + 1}] ---")
        print(output)
        print("------------------------")
        
        # Check if agent is done
        if "Final Answer:" in output:
            final = output.split("Final Answer:")[-1].strip()
            return final, iteration + 1
        
        # Parse tool call
        if "Action:" in output and "Action Input:" in output:
            try:
                action = output.split("Action:")[1].split("\n")[0].strip()
                action_input = output.split("Action Input:")[1].split("\n")[0].strip()
                
                # Execute tool
                if action == "rag_search":
                    result = tool_rag_search(action_input, index, model, util)
                    tool_output = json.dumps(result)
                elif action == "get_policy_by_title":
                    result = tool_get_policy_by_title(action_input, index)
                    tool_output = json.dumps(result)
                elif action == "summarise_text":
                    tool_output = tool_summarise_text(action_input)
                else:
                    tool_output = f"Unknown tool: {action}"
            except Exception as e:
                tool_output = f"Error processing action parsing: {str(e)}"
            
            # ⚠️ Log the tool's return output as well
            print(f"⚙️ [TOOL OUTPUT]: {tool_output[:150]}...")
            
            # Add tool result to conversation
            messages.append({
                "role": "user", 
                "content": f"Tool result: {tool_output}"
            })
    
    return "Agent could not complete the task within iteration limit.", max_iterations