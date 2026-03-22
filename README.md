This armenian costumer support agent listens and answers with voice to questions about credits, deposits, branches of 3 banks(AmeriaBank, FastBank, IDBank).

User voice input->STT(Google Speech Recognition)->Langchain agent+RAG(ChromaDB)->Llama 3.1 via Groq->TTS(Openai TTS)->voice response

//How to use
1. Clone the repository

git clone https://github.com/Emmasahakyan/bank_costumer_support_agent.git
cd bank_costumer_support_agent

2. Create Virtual environment

python -m venv venv

venv\Scripts\activate (Windows)
source venv/bin/activate  (Mac)

3.Install dependencies

pip install -r requirements.txt

4.Create .env file

GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key

5.Scrape bank websites

python scrape_and_save.py

(adding new bank only requires adding URLs)

6.Build vector db

python build_vectorspace.py

7. run the agent
 
python main.py
