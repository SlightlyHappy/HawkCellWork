Redacted sensitive information (tho even if you find something it's behind logins/authentication so good luck), but a bunch of different things I took on while at HawkCell. 
One of the python scripts can try to fill in an excel based on whats missing in a row and what the headers of the table are. So step by step : it grabs headers pushes then to AI API then forms context, then goes row by row to get missing values, then tries to relate missing values to context to find appropriate/close value. 
What can be improved - the prompt needs to be improved - right now it step is not well defined for the AI (learned about prompt engineering and now feel stupid all over again - cus that makes so much sense, why did I disregard it?). 
                    - Maybe adjust the steps a bit so that multiple chats are initiatied? Change order of steps completly - have groups of rows be checked for missing values form context - then form context with header, then compare contexts to fill rows? 


Includes steps.py for zapier (folder needs to be really organized)... 

And some other stuff
