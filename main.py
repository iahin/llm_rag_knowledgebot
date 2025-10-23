from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

model = OllamaLLM(model="llama3.2", temperature=0.7)

template = """
You are an expert in answering question about a pizza restaurent.

Here are some relevant reviews: {reviews}

here is the question ti answer: {question}

"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

while True:
    print("--------------------------------")
    question = input("Please enter your question about the pizza restaurant (or type 'exit' to quit): ")
    
    print("\n\n")
    
    if question.lower() == 'exit':
        break
    
    reviews = retriever.invoke(question)
    result = chain.invoke({
        "reviews": reviews, 
        "question": question})

    print(result)