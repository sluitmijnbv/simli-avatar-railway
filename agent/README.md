\# SIMLI + LIVEKIT + OPENAI AVATAR (Backend Worker)



This folder contains the Python worker that manages:

\- LiveKit agent room logic

\- OpenAI Realtime LLM

\- Simli avatar connection



Deploy via Railway:



1\. Create a Railway project

2\. Add Service → GitHub Repo

3\. Set environment variables:

&nbsp;  - SIMLI\_API\_KEY

&nbsp;  - SIMLI\_FACE\_ID

&nbsp;  - OPENAI\_API\_KEY

&nbsp;  - LIVEKIT\_URL

&nbsp;  - LIVEKIT\_API\_KEY

&nbsp;  - LIVEKIT\_API\_SECRET

4\. Deploy



The worker launches automatically and joins the LiveKit room for avatar interaction.



